import sys
import json
import os
import random
import time
from pathlib import Path

class Agent():
    # This agent is made for basic tests. He makes random actions just to test all the game methods.
    
    state = 'waiting' # states may be: waiting | attacking | conquering | fortifying | mobilizing 
    player_data = {}

    def __init__(self, id):
        self.id = int(id)

        self.calls_path = Path('Calls/player_' + str(id) + '.json')
        self.data_path = Path('Logs/player_' + str(id) + '.json')

        self.last_time = os.path.getmtime(self.data_path)

        self.player_data_count = 0

        self.call_data = {
            'id': id,
            'count': 0,
            'command': {
                'name': '',
                'args': []
        }  
    }

    def wait_game(self):
        """
        wait until data_path is updated
        """
        current_time = os.path.getmtime(self.data_path)

        last_count = self.player_data_count

        while True:
            while self.last_time == current_time:
                current_time = os.path.getmtime(self.data_path)

            self.last_time = os.path.getmtime(self.data_path)

            if self._file_changed(last_count):
                break

    def mobilize(self):
        """
        Randomly distribute troops among owned countries until player has 0 new troops
        """
        if(self.player_data['n_new_troops'] == 0):
            self._call_action('pass_turn', [])
        else:
            action = 'set_new_troops'
            args = [random.randint(1, self.player_data['n_new_troops']), random.choice(self.player_data['countries_owned'])]
            self._call_action(action, args)

    def attack(self):

        list_borders = list(self.player_data['border_countries'].keys())

        random.shuffle(list_borders)

        for country_name in list_borders:
            for enemy_name in self.player_data['border_countries'][country_name]:

                if self.player_data['countries_data'][country_name]['n_troops'] > 1:
                    #if self.player_data['countries_data'][country_name]['n_troops'] > self.player_data['countries_data'][enemy_name]['n_troops']:

                    action = 'attack'

                    if self.player_data['countries_data'][country_name]['n_troops'] == 2:
                        n_dice = 1
                    elif self.player_data['countries_data'][country_name]['n_troops'] == 3:
                        n_dice = 2
                    elif self.player_data['countries_data'][country_name]['n_troops'] >= 4:
                        n_dice = 3
                    
                    args = [n_dice, country_name, enemy_name]
                    self._call_action(action, args)
                    return

        self._pass_turn()             
            
    def conquer(self):
        """
        Move a random number of troops between two owned countries, being the sender the winner of the attack made last turn and the receiver the loser
        """
        from_country = self.call_data['command']['args'][1]
        to_country = self.call_data['command']['args'][2]

        n_available_troops = self.player_data['countries_data'][from_country]['n_troops']

        action = 'move_troops'
        args = [random.randrange(n_available_troops), from_country, to_country]

        self._call_action(action, args)

    def fortify(self):
        """
        This bot does fortify already
        """
        country_1 = None
        for _ in range(10):
            country_1 = random.choice(self.player_data['countries_owned'])
            if self.player_data['countries_data'][country_1]['n_troops'] > 1:
                break
            country_1 = None
        
        if country_1 != None:
            for country_2 in self.player_data['countries_owned']:
                if country_1 == country_2:
                    continue
                elif self.player_data['connection_matrix'][country_1][country_2] == True:
                    action = 'move_troops'
                    n_troops = random.randrange(self.player_data['countries_data'][country_1]['n_troops'])
                    args = [n_troops, country_1, country_2]
                    self._call_action(action, args)
                    return
            
        self._pass_turn()

    def _file_changed(self, last_count):
        while True:
            try:
                with open(self.data_path) as openfile:
                    data = json.load(openfile)
                    if data["count"] == last_count:
                        #print("Atualizou sem precisar")
                        return False
                    else:
                        self.player_data_count = data["count"]
                        self._get_game_data(data)
                        return True
            except:
                pass

    def _get_game_data(self, data):
        self.player_data = data
        self.state = self.player_data['state']


    def _call_action(self, action: str, args: list):
        # print('Next move')
        # input()
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

        # self._log()

    def _pass_turn(self):
        self._call_action('pass_turn', [])

    def _log(self):
        if self.call_data['command']['name'] == 'attack':
            print('Attacked', self.call_data['command']['args'][2], 'with', self.call_data['command']['args'][1], 'using', self.call_data['command']['args'][0], 'troops')
        elif self.call_data['command']['name'] == 'move_troops':
            print('Moved', self.call_data['command']['args'][0], 'troops from', self.call_data['command']['args'][1], 'to', self.call_data['command']['args'][2])
        elif self.call_data['command']['name'] == 'set_new_troops':
            print('Setted', self.call_data['command']['args'][0], 'new troops in', self.call_data['command']['args'][1])
        elif self.call_data['command']['name'] == 'pass_turn':
            print('Passed the turn')
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please pass your player id as argument")
        quit()

    if int(sys.argv[1]) != 1 and int(sys.argv[1]) != 2:
        print("Please choose between id 1 or 2")
        quit()

    agent = Agent(sys.argv[1])

    while True:
        if agent.state == 'waiting':
            agent.wait_game()
        elif agent.state == 'attacking':
            agent.attack()
        elif agent.state == 'conquering':
            agent.conquer()
        elif agent.state == 'fortifying':
            agent.fortify()
        elif agent.state == 'mobilizing':
            agent.mobilize()
        elif agent.state == 'winner':
            #print('I am surprised this actualy worked')
            quit()
        elif agent.state == 'loser':
            #print('This was expected')
            quit()
        else:
            print('State unknown')