from world import World
from player import Player
from country import Country

import sys
import time
import json
import random
import os
from pathlib import Path

class Game:
    """Runs the game, providing an interface for the players to play the game\\
    within the rules.

    Parameters
    ----------
    log : bool
        True to print logs with the actions taken on the game.
    
    Attributes
    ----------
    player_1 : Player
        An instance of Player that keeps all the player 1 data, states,
        and is used to call invoke its actions.
    player_2 : Player
        An instance of Player that keeps all the player 2 data, states,
        and is used to call invoke its actions.
    active_player : Player
        The instance of the Player that is currently taking an action.
    winner : Player or None
        The instance of the Player that won the game. If no one won the game
        yet, it will return None.
    map_changed : bool
        True if the map was changed by the last action made by a player.

    Methods
    -------
    update_players_data()

    wait_for_agent(player : Player)

    execute_player_action(id : int)

    """

    def __init__(self, log=False):
        self.world = World('worlds/classic.json')
        self.player_1 = Player(1,40)
        self.player_2 = Player(2,40)

        self.turn = 0

        coin = random.randint(1,2)
        self.player_1.state = "mobilizing" if coin == 1 else "waiting"
        self.player_2.state = "mobilizing" if coin == 2 else "waiting"
        self.active_player = self.player_1 if coin == 1 else self.player_2

        self.player_1.control.call_count = 0
        self.player_2.control.call_count = 0
        
        self.player_1.control.call_path = Path("Calls/player_1.json")
        self.player_2.control.call_path = Path("Calls/player_2.json")
        
        self.player_1.control.data_path = Path("Logs/player_1.json")
        self.player_2.control.data_path = Path("Logs/player_2.json")

        self.winner = None
        self.map_changed = True
        self.log = log

        self._setup()

    def _setup(self):
        self._create_command_files()
        self._random_draft()
        self._distribute_new_troops(self.active_player)
        self._update_continents_owners()
        self.update_players_data()

    def _distribute_new_troops(self, player : Player):
        """Distribute new troops to a player based on the number of countries\\
        owned and what continents owned.

        Parameters
        ----------
        player : Player
            The `Player` object that will receive the new troops
        """

        n_countries_owned = len(player.countries_owned)
        n_new_troops = int(n_countries_owned // 3)
        n_new_troops = max(n_new_troops, 3)

        bonus_troops = 0

        for continent in self.world.continents:
            if continent.owner == player:
                bonus_troops += continent.extra_armies
        
        #print("Total bonus = ", bonus_troops)

        n_new_troops += bonus_troops
        player.n_new_troops += n_new_troops
        

    def _create_call_data(self, id: int, call_count: int) -> str:
        """Create the json data structure to be written inside a call file.

        Parameters
        ----------
        id : int
            An `int` with the player's id who is owner of the call file.
        call_count : int
            An `int` with a counter of calls made by the owner of the call file.

        Returns
        -------
        json_data : str
            A `string` with the data to be written in a json file.
        """

        data = {
            'id': id,
            'count': call_count,
            'command': {
                'name': "",
                'args': []
            }  
        }

        json_data = json.dumps(data, indent = 4)
        
        return json_data

    # TODO Make a _update_countries_data where it updates only the changeable data
    def _create_countries_data(self) -> dict:
        """Create a dict with info about all countries

        Returns
        -------
        countries_data : dict
        """

        countries_data = {} 

        for country in self.world.country_list:
            countries_data[country.name] = {
                "neighbours": [neighbour.name
                               for neighbour 
                               in country.neighbours],
                "owner": country.owner.id,
                "n_troops": country.n_troops
            }

        return countries_data

    # TODO Make a _update_continents_data where it updates only the changeable data
    def _create_continents_data(self) -> dict:
        """Create a dict with info about all continents

        Returns
        -------
        continents_data : dict
        """

        continents_data = {}

        for continent in self.world.continents:
            continent_owner = None
            
            if continent.owner != None:
                continent_owner = continent.owner.id

            continents_data[continent.name] = {
                "owner": continent_owner,
                "extra_armies": continent.extra_armies,
                "countries": [country.name for country in continent.countries]
            }

        return continents_data

    def _is_connected(
            self,
            country_1: Country,
            country_2: Country,
            countries_visited: list=None
        ) -> bool:
        """Check if two countries are connected by allied countries.

        Parameters
        ----------
        country_1 : Country
        country_2 : Country
        countries_visited : list, default [country_1]

        Returns
        -------
        bool
            `True` if the countries have a connection

            `False` if the countries don't have a connection
        """

        if countries_visited is None:
            countries_visited = [country_1]
        for neighbour in country_1.neighbours:
            if neighbour in countries_visited:
                continue
            elif neighbour.owner == country_1.owner:
                if neighbour == country_2:
                    return True
                else:
                    countries_visited.append(neighbour)
                    if self._is_connected(neighbour, country_2, countries_visited):
                        return True
        return False

    def _create_connection_matrix(self, player : Player):
        """Create a matrix that tells if there is a land connection between\\
        allied countries.

        E.g.: `connection_matrix['country A']['country B'] = True`

        Parameters
        ----------
        player : Player
            The `Player` object owner of the countries that are in the matrix.
        """

        player.connection_matrix = {} 

        for country in player.countries_owned:
            player.connection_matrix[country.name] = {}
        
        for country_1 in player.countries_owned:
            for country_2 in player.countries_owned:
                if country_1 == country_2:
                    continue
                elif (country_1, country_2) in player.connection_matrix.items():
                    continue
                else:
                    if self._is_connected(country_1, country_2):
                        player.connection_matrix[country_1.name][country_2.name] = True
                        player.connection_matrix[country_2.name][country_1.name] = True
                    else:
                        player.connection_matrix[country_1.name][country_2.name] = False
                        player.connection_matrix[country_2.name][country_1.name] = False

    def _create_border_countries(self, player : Player):
        """Create a dict containing countries as keys and enemy neighbours as\\
        values.

        E.g.: `{'country A': ['enemy neighbour B', 'enemy neighbour C', ...]}`

        Parameters
        ----------
        player : Player
            The `Player` object owner of the countries used as keys.
        """

        player.border_countries = {}

        for country in player.countries_owned:
                for neighbour in country.neighbours:
                    if neighbour.owner != player:
                        if country.name not in player.border_countries:
                            player.border_countries[country.name] = []
                            player.border_countries[country.name].append(neighbour.name)
                        else:
                            player.border_countries[country.name].append(neighbour.name)

    # TODO use the update_continent_owner method of the Continent class
    def _update_continents_owners(self):
        """Iterate over all the countries of each continent checking its\\
        owners and updating each continent's owner according to that.
        """

        for continent in self.world.continents:
            continent_owner = None
            for country in continent.countries:
                if continent_owner == None:
                    continent_owner = country.owner
                elif country.owner != continent_owner:
                    continent_owner = None
                    break
            continent.owner = continent_owner
            
    def _create_player_data(
            self,
            continents_data: dict,
            countries_data: dict,
            player: Player
        ) -> str:
        """Create the json data structure to be written inside a log file.

        Parameters
        ----------
        continents_data : dict
            A `dict` with all the continents as keys and their info as values.
        countries_data : dict
            A `dict` with all the countries as keys and their info as values.
        player : Player
            The `Player` object owner of the data
            
        Returns
        -------
        json_data : str
            A `string` with the data to be written in a json file.
        """

        countries_owned_names = [country.name
                                 for country
                                 in player.countries_owned]

        player.data_count += 1

        if self.map_changed:
            self._create_border_countries(player)
            self._create_connection_matrix(player)

        if player.id == 1:
            enemy = self.player_2
        else:
            enemy = self.player_1

        data = {
            "count": player.data_count,
            "id": player.id,
            "n_new_troops": player.n_new_troops,
            "n_total_troops": player.n_total_troops,
            "enemy_n_total_troops": enemy.n_total_troops,
            "state": player.state,
            "countries_owned": countries_owned_names,
            "countries_data": countries_data,
            "border_countries": player.border_countries,
            "connection_matrix": player.connection_matrix,
            "continents_data": continents_data
        }

        json_data = json.dumps(data, indent = 4)

        return json_data

    def _create_command_files(self):
        """Create p1 and p2 command files used to declare their actions."""

        p1_json_data = self._create_call_data(1, self.player_1.control.call_count)
        p2_json_data = self._create_call_data(2, self.player_2.control.call_count)

        with open(self.player_1.control.call_path, "w") as f: 
            f.write(p1_json_data)
        self.last_m_time_p1 = os.path.getmtime(self.player_1.control.call_path)
        
        with open(self.player_2.control.call_path, "w") as f:
            f.write(p2_json_data)
        self.last_m_time_p2 = os.path.getmtime(self.player_2.control.call_path)

    def _random_draft(self):
        """Randomly distribute countries and troops between players."""

        random.shuffle(self.world.country_list)

        self.player_1.countries_owned = self.world.country_list[0:21]
        self.player_2.countries_owned = self.world.country_list[21:42]

        for country in self.player_1.countries_owned:
            country.owner = self.player_1
            self.player_1.set_new_troops(1, country)

        for country in self.player_2.countries_owned:
            country.owner = self.player_2
            self.player_2.set_new_troops(1, country)

        # Distribute troops randomly among countries owned
        while self.player_1.n_new_troops > 0:
            country = random.choice(self.player_1.countries_owned)
            self.player_1.set_new_troops(random.randint(0, self.player_1.n_new_troops), country)
        
        while self.player_2.n_new_troops > 0:
            country = random.choice(self.player_2.countries_owned)
            self.player_2.set_new_troops(random.randint(0, self.player_2.n_new_troops), country)

    def update_players_data(self):
        """Update players' data files with all the current game states."""

        countries_data = self._create_countries_data()
        continents_data = self._create_continents_data()

        p1_json_data = self._create_player_data(continents_data, countries_data, self.player_1)
        p2_json_data = self._create_player_data(continents_data, countries_data, self.player_2)

        with open(self.player_1.control.data_path, "w") as f:
            f.write(p1_json_data)
        with open(self.player_2.control.data_path, "w") as f:
            f.write(p2_json_data)

    def wait_for_agent(self, player: Player):
        """Wait for the player's declaration of action.
        
        Parameters
        ----------
        player : Player
            The `player` that is currently making an action.
        """

        current_time = os.path.getmtime(player.control.call_path)

        last_count = player.control.call_count

        while last_count == player.control.call_count:
            while player.control.last_m_time == current_time:
                current_time = os.path.getmtime(player.control.call_path)

            while True:
                try:
                    with open(player.control.call_path) as openfile:
                        call_data = json.load(openfile)
                        if call_data["count"] == player.control.call_count:
                            #print("Atualizou sem precisar")
                            pass
                        else:
                            player.control.last_call_data = player.control.call_data
                            player.control.call_data = call_data
                        player.control.call_count = call_data["count"]
                        break
                except:
                    #print("Oh, deu erro aqui")
                    pass

            current_time = os.path.getmtime(player.control.call_path)

            player.control.last_m_time = current_time

    def _attack(self, player: Player, enemy: Player):
        """Performs an attack action from one player to other.

        Parameters
        ----------
        player : Player
            The `player` performing the action.
        enemy : Player        
            The `player` suffering the action.
        """

        attacker = None
        attacked = None

        for country_owned in player.countries_owned:
            if country_owned.name == player.control.call_data["command"]["args"][1]:
                attacker = country_owned
                break
        
        for country_owned in enemy.countries_owned:
            if country_owned.name == player.control.call_data["command"]["args"][2]:
                attacked = country_owned
                break        
        
        if(attacker == None):
            print("Player", player.id, "does not own any country named", player.control.call_data["command"]["args"][1])
        elif(attacked == None):
            print("Player", enemy.id, "does not own any country named", player.control.call_data["command"]["args"][2])
        else:
            attacker_n_troops_before_attack = attacker.n_troops
            attacked_n_troops_before_attack = attacked.n_troops

            has_won = player.attack(player.control.call_data["command"]["args"][0], attacker, attacked)

            attacker_troops_after = attacker_n_troops_before_attack - attacker.n_troops
            attacked_troops_after = attacked_n_troops_before_attack - attacked.n_troops

            attacker.owner.n_total_troops -= attacker_troops_after
            attacked.owner.n_total_troops -= attacked_troops_after

            if has_won:
                enemy.countries_owned.remove(attacked)
                player.countries_owned.append(attacked)
                attacked.owner = attacker.owner
                attacked.n_troops += player.control.call_data["command"]["args"][0]
                attacker.n_troops -= player.control.call_data["command"]["args"][0]
                player.state = "conquering"

                if len(player.countries_owned) == 42:
                    self.winner = player

                self._update_continents_owners()
            
            self.map_changed = has_won

    # TODO Maybe the enemy player is not needed
    def _move_troops(self, player : Player, enemy : Player):
        """Performs a move troops action from one player.

        Parameters
        ----------
        player : Player
            The `player` performing the action.
        enemy : Player        
            The other `player`. 
        """

        from_country = None
        to_country = None

        if player.state == 'conquering':
            if player.control.call_data['command']['args'][1] != player.control.last_call_data['command']['args'][1] or player.control.call_data['command']['args'][2] != player.control.last_call_data['command']['args'][2]:
                print("Player", player.id, "can only move between", player.control.last_call_data['command']['args'][1], "and", player.control.last_call_data['command']['args'][2], "during a conquering")
                return

        if player.state == 'fortifying':
            country_1 = player.control.call_data["command"]["args"][1]
            country_2 = player.control.call_data["command"]["args"][2]
            if not player.connection_matrix[country_1][country_2]:
                print("Player", player.id, "is trying to mobilize troops between countries not connected (", country_1, "-", country_2, ")")
                return
            

        for country_owned in player.countries_owned:
            if country_owned.name == player.control.call_data["command"]["args"][1]:
                from_country = country_owned
                break
        
        for country_owned in player.countries_owned:
            if country_owned.name == player.control.call_data["command"]["args"][2]:
                to_country = country_owned
                break
        
        if(from_country == None):
            print("Player", player.id, "does not own any country named", player.control.call_data["command"]["args"][1])
        elif(to_country == None):
            print("Player", enemy.id, "does not own any country named", player.control.call_data["command"]["args"][2])
        else:
            player.move_troops(player.control.call_data["command"]["args"][0], from_country, to_country)

            if player.state == "conquering":
                player.state = "attacking"

            elif player.state == "fortifying":
                self._pass_turn(player, enemy)

    def _set_new_troops(self, player : Player):
        """Performs a set new troops action from one player.

        Parameters
        ----------
        player : Player
            The `player` performing the action.
        """

        country = None

        for country_owned in player.countries_owned:
            if country_owned.name == player.control.call_data["command"]["args"][1]:
                country = country_owned
                break
        
        if(country == None):
            print("Player", player.id, "does not own any country named", player.control.call_data["command"]["args"][1])
        else:
            player.set_new_troops(player.control.call_data["command"]["args"][0], country)

    def _pass_turn(self, player : Player, enemy : Player):
        """Performs the action of passing the turn to another player.

        Parameters
        ----------
        player : Player
            The `player` performing the action.
        enemy : Player        
            The `player` that will play in the next turn.
        """

        if player.state == "mobilizing":
            player.state = "attacking"

        elif player.state == "attacking":
            player.state = "fortifying"

        elif player.state == "fortifying":
            player.state = "waiting"
            self.turn = self.turn + 1
            self.active_player = enemy
            enemy.state = "mobilizing"
            self._distribute_new_troops(self.active_player)

        elif player.state == "conquering":
            print("Player", player.id, "cannot pass_turn during a conquering state")

    def execute_player_action(self, player : Player):
        """Read the call_data of the player and perform the action wrote on it.

        Parameters
        ----------
        player : Player
            The `Player` object that is performing the action.
        """

        self.map_changed = False

        enemy = self.player_2 if player.id == 1 else self.player_1

        call_data = player.control.call_data

        if self.log:
            print(call_data)
                
        if call_data["command"]["name"] == "attack":
            self._attack(player, enemy)
        
        elif call_data["command"]["name"] == "move_troops":
            self._move_troops(player, enemy) 

        elif call_data["command"]["name"] == "set_new_troops":
            self._set_new_troops(player)
        
        elif call_data["command"]["name"] == "pass_turn":
            self._pass_turn(player, enemy)

        else:
            print("Player", player.id, "is trying to use a command that does not exist (", call_data["command"]["name"], ")")

        #print('Player:', id, 'count:', call_data['count'])

def print_game_result(game: Game, game_duration: int):
    winner_txt = f'Winner: P{game.winner.id}'
    n_troops_txt = f'Number of Troops on the Board: {game.winner.n_total_troops}'
    p1_n_actions = f'P1 Number of Actions: {game.player_1.control.call_count}'
    p2_n_actions = f'P2 Number of Actions: {game.player_2.control.call_count}'
    n_game_turns = f'Number of Game Turns: {game.turn}'
    game_duration_txt = f'Time: {game_duration}'

    print(winner_txt)
    print(n_troops_txt)
    print(p1_n_actions)
    print(p2_n_actions)
    print(n_game_turns)
    print(game_duration_txt)

if __name__ == '__main__':
    start_time = time.perf_counter()
    game = Game(log=False)

    while game.turn < 150:
        game.wait_for_agent(game.active_player)

        game.execute_player_action(game.active_player)

        if game.winner != None:
            game_duration = time.perf_counter() - start_time
            print_game_result(game, game_duration)
            
            if game.winner.id == 1:
                game.player_1.state = "winner"
                game.player_2.state = "loser"

            elif game.winner.id == 2:
                game.player_1.state = "loser"
                game.player_2.state = "winner"
            
            game.update_players_data()
            game.turn += 1
            break
                
        game.update_players_data()