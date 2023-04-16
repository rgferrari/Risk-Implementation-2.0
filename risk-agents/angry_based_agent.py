from agent_base import AgentBase
import sys


class AngryBased(AgentBase):
    """
    This is a model of an Agent class based on sillysoft's Angry agent's heuristic
    """
    def __init__(self, id: int):
        super().__init__(id)
    
    def _get_n_enemies_beside(self, country: str) -> int:
        country_enemies_beside = 0
        for neighbour in self.player_data['countries_data'][country]['neighbours']:
            if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                country_enemies_beside += self.player_data['countries_data'][neighbour]['n_troops']
        
        return country_enemies_beside

    """
    Check all countries owned and remember the one with most enemy troops beside
    """
    def mobilize(self):
        if(self.player_data['n_new_troops'] == 0):
            self._pass_turn()
        else:
            chosen_country = None
            chosen_country_enemies_beside = 0

            for country in self.player_data['countries_owned']:
                country_enemies_beside = self._get_n_enemies_beside(country)
                
                if country_enemies_beside > chosen_country_enemies_beside:
                    chosen_country_enemies_beside = country_enemies_beside
                    chosen_country = country
            
            action = 'set_new_troops'
            args = [self.player_data['n_new_troops'], chosen_country]
            self._call_action(action, args)

    def attack(self):
        # Will attack an enemy until death
        # Check if attacked an enemy last round and if the enemy is still attackable
        if self.call_data['command']['name'] == 'attack':
            last_country_attacking = self.call_data['command']['args'][1]
            last_enemy_attacked = self.call_data['command']['args'][2]
            if self.player_data['countries_data'][last_enemy_attacked]['owner'] != self.id:
                if self.player_data['countries_data'][last_country_attacking]['n_troops'] >= 2:
                    action = 'attack'

                    if self.player_data['countries_data'][last_country_attacking]['n_troops'] == 2:
                        n_dice = 1
                    elif self.player_data['countries_data'][last_country_attacking]['n_troops'] == 3:
                        n_dice = 2
                    elif self.player_data['countries_data'][last_country_attacking]['n_troops'] >= 4:
                        n_dice = 3
                    
                    args = [n_dice, last_country_attacking, last_enemy_attacked]

                    self._call_action(action, args)
                    return

        countries_able_to_attack = []

        # Check all countries owned that are able to attack
        for country in self.player_data['countries_owned']:
            if self.player_data['countries_data'][country]['n_troops'] >= 2:
                countries_able_to_attack.append(country)

        for country in countries_able_to_attack:
            weakest_neighbour = None
            weakest_neighbour_n_troops = float('inf')

            # Search for country's weakest neighbour
            for neighbour in self.player_data['countries_data'][country]['neighbours']:
                if self.player_data['countries_data'][neighbour]['owner'] != self.id:
                    if self.player_data['countries_data'][neighbour]['n_troops'] < weakest_neighbour_n_troops:
                        weakest_neighbour = neighbour
                        weakest_neighbour_n_troops = self.player_data['countries_data'][neighbour]['n_troops']
            
            # If have more troops than the weakest neighbour, attack
            if weakest_neighbour != None and self.player_data['countries_data'][country]['n_troops'] > weakest_neighbour_n_troops:
                action = 'attack'

                if self.player_data['countries_data'][country]['n_troops'] == 2:
                    n_dice = 1
                elif self.player_data['countries_data'][country]['n_troops'] == 3:
                    n_dice = 2
                elif self.player_data['countries_data'][country]['n_troops'] >= 4:
                    n_dice = 3
                
                args = [n_dice, country, weakest_neighbour]

                self._call_action(action, args)
                return
        
        self._pass_turn()

    def conquer(self):
        from_country = self.call_data['command']['args'][1]
        to_country = self.call_data['command']['args'][2]

        n_available_troops = self.player_data['countries_data'][from_country]['n_troops']

        if self._get_n_enemies_beside(from_country) > self._get_n_enemies_beside(to_country):
            action = 'move_troops'
            args = [0, from_country, to_country]
        else:
            action = 'move_troops'
            args = [n_available_troops - 1, from_country, to_country]

        self._call_action(action, args)

    def fortify(self):
        for country in self.player_data['countries_owned']:
            # if have a moveable troop
            if self.player_data['countries_data'][country]['n_troops'] > 1:
                reacheable_countries = []
                # get all reacheable countries
                for country_owned in self.player_data['countries_owned']:
                    if country != country_owned:
                        if self.player_data['connection_matrix'][country][country_owned]:
                            reacheable_countries.append(country_owned)

                n_enemies_beside = self._get_n_enemies_beside(country)
                
                # for every reacheable country, check if thre are more enemies beside than the origin country
                # if yes, fortify
                for destination_country in reacheable_countries:
                    destination_country_n_enemies_beside = self._get_n_enemies_beside(destination_country)

                    if destination_country_n_enemies_beside > n_enemies_beside:
                        action = 'move_troops'
                        n_troops = self.player_data['countries_data'][country]['n_troops'] - 1
                        args = [n_troops, country, destination_country]
                        self._call_action(action, args)
                        return 
                                           
        self._pass_turn()

if __name__ == "__main__":
    id = AgentBase.read_id(sys.argv)

    agent = AngryBased(id)

    agent.play()