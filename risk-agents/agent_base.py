import sys
import json
import os
from pathlib import Path

class AgentBase():
    """
    This is a model of an Agent class made to play the Risk game
    
    Modify the attack, mobilize, conquer and fortify methods to build your AI

    All the other methods are made to write and read data from the game, let them as they are
    """

    state = 'waiting' # states can be: waiting | attacking | conquering | fortifying | mobilizing 
    player_data = {}

    def __init__(self, id: int):
        self.id = id

        self.log = False

        self.calls_path = Path('Calls/player_' + str(id) + '.json')
        self.data_path = Path('Logs/player_' + str(id) + '.json')

        # These two are used to check if the player data file was modified
        self.last_time = os.path.getmtime(self.data_path)
        self.player_data_count = 0

        # This is the format a call file must have
        self.call_data = {
            'id': id,
            'count': 0,
            'command': {
                'name': '',
                'args': []
        }  
    }

    def _get_player_data(self, data: dict):
        """Save the player data and the actual player state
        
        Parameters
        ----------
        data: dict
            The data read from the player json file given by the game

        Returns
        -------
        None
        """

        self.player_data = data
        self.state = self.player_data['state']

    def _file_changed(self, last_count: int) -> bool:
        """Check if the player json was changed
        
        Parameters
        ----------
        last_count: int
            A counter used to check if the file was modified

        Returns
        -------
        bool
        """

        while True:
            try:
                with open(self.data_path) as openfile:
                    data = json.load(openfile)
                    if data["count"] == last_count:
                        #print("Atualizou sem precisar")
                        return False
                    else:
                        self.player_data_count = data["count"]
                        self._get_player_data(data)
                        return True
            except:
                pass

    def _log(self):
        """Print on the terminal the action the bot asked for the player to execute"""

        if self.call_data['command']['name'] == 'attack':
            print('Attacked', self.call_data['command']['args'][2], 'with', self.call_data['command']['args'][1], 'using', self.call_data['command']['args'][0], 'troops')
        elif self.call_data['command']['name'] == 'move_troops':
            print('Moved', self.call_data['command']['args'][0], 'troops from', self.call_data['command']['args'][1], 'to', self.call_data['command']['args'][2])
        elif self.call_data['command']['name'] == 'set_new_troops':
            print('Setted', self.call_data['command']['args'][0], 'new troops in', self.call_data['command']['args'][1])
        elif self.call_data['command']['name'] == 'pass_turn':
            print('Passed the turn')

    def _call_action(self, action: str, args: list):
        """
        Write a command to the call file

        After this method the game will process the action called

        Because of that, only call this method when your method has nothing more to do

        Parameters
        ----------
        action : str
            The action name (attack | move_troops | set_new_troops | pass_turn)
        args : list
            A list with the args of the given action. The args of each action must be:
            
            attack: [n_dice: int, attacker: str, attacked: str]

            move_troops: [n_troops: int, from_country: str, to_country: str] 

            set_new_troops: [n_troops: int, country_name: str]

            pass_turn: []

        Returns
        -------
        None
        """

        with open(self.calls_path, 'w') as outfile:
            self.call_data = {
                'id': self.id,
                'count': self.call_data['count'] + 1,
                'command': {
                    'name': action,
                    'args': args
                }  
            }

            json_obj = json.dumps(self.call_data)

            outfile.write(json_obj)

        self.state = 'waiting'

        if self.log:
            self._log()
    
    def _pass_turn(self):
        """Ask the _call_action() method to pass the turn """
        self._call_action('pass_turn', [])

    def wait_game(self):
        """Wait until data_path is updated. If it is, save the new player data and state"""
        current_time = os.path.getmtime(self.data_path)

        last_count = self.player_data_count

        while True:
            while self.last_time == current_time:
                current_time = os.path.getmtime(self.data_path)

            self.last_time = os.path.getmtime(self.data_path)

            if self._file_changed(last_count):
                break

    def win(self):
        quit()

    def lose(self):
        quit()

    @staticmethod
    def read_id(args):
        if len(args) != 2:
            print("Please pass your player id as argument")
            quit()

        id = int(args[1])

        if id != 1 and id != 2:
            print("Please choose between id 1 or 2")
            quit()

        return id

    def play(self):
        while True:
            if self.state == 'waiting':
                self.wait_game()
            elif self.state == 'attacking':
                self.attack()
            elif self.state == 'conquering':
                self.conquer()
            elif self.state == 'fortifying':
                self.fortify()
            elif self.state == 'mobilizing':
                self.mobilize()
            elif self.state == 'winner':
                self.win()
            elif self.state == 'loser':
                self.lose()
            else:
                print('State unknown')
    
    # Modify the next four methods to implement your AI
    
    def attack(self):
        """decides what to do when state is attacking"""
        pass

    def mobilize(self):
        """decides what to do when state is mobilizing"""
        pass

    def conquer(self):
        """decides what to do when state is conquering"""
        pass

    def fortify(self):
        """decides what to do when state is fortifying"""
        pass
    
if __name__ == "__main__":
    id = AgentBase.read_id(sys.argv)

    agent = AgentBase(id)

    agent.play()