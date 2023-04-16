from ast import AsyncFunctionDef
from cluster_based_agent import ClusterBased
from pathlib import Path
import json
import sys
import os
import math
import random

class MonteCarlo(ClusterBased):
    def __init__(self, id: int):
        super().__init__(id)
        self.log = False
        # The tree with all the other games subtrees
        self.tree_path = Path('Risk-Agents/montecarlo_tree.json')
        self.tree = self._get_game_tree()
        self.subtree = []
        self.searching_state = 'exploiting' # can be exploiting or exploring

    def _get_game_tree(self) -> dict:
        print('vai pegar a arvore')
        if not os.path.isfile(self.tree_path):
            return {}

        while True:
            try:
                with open(self.tree_path) as openfile:
                    tree = json.load(openfile)
                    print('leu a arvore')
                    return tree
            except:
                print('ta dando erro')
                pass

    def _update_game_tree_file(self):
        with open(self.tree_path, 'w') as outfile:
            json_obj = json.dumps(self.tree)
            outfile.write(json_obj)

    def _get_node_id(self, state: dict) -> str:
        id = len(self.tree) + 1
        id = str(id)

        for node_id in self.tree.keys():
            node_state = self.tree[node_id]['state']

            is_different = False

            for player in node_state.keys():
                if is_different:
                    break
                for country in node_state[player].keys():
                    if country in state[player]:
                        if node_state[player][country] != state[player][country]:
                            is_different = True
                            break
                    else:
                        is_different = True
                        break   
            
            if not is_different:
                return node_id

        return id

    def _get_enemy_countries(self) -> list:
        enemy_countries = []

        continents = self.player_data['continents_data'].keys()
        for continent in continents:
            countries = self.player_data['continents_data'][continent]['countries']
            for country in countries:
                country_owner = self.player_data['countries_data'][country]['owner']
                if country_owner != self.id:
                    enemy_countries.append(country)
        
        return enemy_countries

    def _create_state(self) -> dict:
        state = {}
        player_countries_troops = {}
        enemy_countries_troops = {}

        countries_owned = self.player_data['countries_owned']

        enemy_countries_owned = self._get_enemy_countries()

        for country_owned in countries_owned:
            player_countries_troops[country_owned] = self.player_data['countries_data'][country_owned]['n_troops']
        
        for enemy_country_owned in enemy_countries_owned:
            enemy_countries_troops[enemy_country_owned] = self.player_data['countries_data'][enemy_country_owned]['n_troops']

        state['player'] = player_countries_troops
        state['enemy'] = enemy_countries_troops

        return state

    def _create_node(self):
        state = self._create_state()
        id = self._get_node_id(state)

        is_new_node = False

        if id not in self.tree:
            self.tree[id] = {}
            self.tree[id]['state'] = state
            self.tree[id]['leafs'] = []
            self.tree[id]['n_visits'] = 0
            self.tree[id]['value'] = 0
            is_new_node = True


        return id, is_new_node

    def _add_to_subtree(self, id: str):
        if self.call_data['command']['name'] == 'attack':
            self.subtree.append([id, self.call_data['command']['args'][1], self.call_data['command']['args'][2]])
        else:
            self.subtree.append([id, 'pass'])

    def _uct(self, id: str, leaf_id: str):
        v = self.tree[leaf_id]['value']
        n = self.tree[leaf_id]['n_visits']
        c = math.sqrt(2) # constante de exploração
        big_n = self.tree[id]['n_visits']

        return (v / n) + c * math.sqrt( ( math.log(big_n) / n ) )

    def _get_countries_that_can_attack(self) -> list:
        border_countries = list(self.player_data['border_countries'].keys())
        countries_that_can_attack = [country for country in border_countries if self.player_data['countries_data'][country]['n_troops'] > 1]

        return countries_that_can_attack

    def _attack_with_everything(self, attacker: str, attacked: str):
        n_troops = self.player_data['countries_data'][attacker]['n_troops']
        
        action = 'attack'
        if n_troops == 2:
            n_dice = 1
        elif n_troops == 3:
            n_dice = 2
        elif n_troops >= 4:
            n_dice = 3
        args = [n_dice, attacker, attacked]
        self._call_action(action, args)

    def _attack_until_end(self) -> bool:
        """Check if is attacking some country and continue the attack"""
        if self.call_data['command']['name'] == 'attack':
            last_country_attacking = self.call_data['command']['args'][1]
            last_enemy_attacked = self.call_data['command']['args'][2]
            # If didnt conquered
            if self.player_data['countries_data'][last_enemy_attacked]['owner'] != self.id:
                # If still can attack
                if self.player_data['countries_data'][last_country_attacking]['n_troops'] >= 2:
                    self._attack_with_everything(last_country_attacking, last_enemy_attacked)
                    return True
        
        return False

    def _explore(self):
        """Do a random attack to explorate a new node"""

        countries = self._get_countries_that_can_attack()
        random.shuffle(countries)

        n_attacks_possibilities = 0
        for country in countries:
            n_attacks_possibilities += len(self.player_data['border_countries'][country])

        if n_attacks_possibilities == 0:
            self._pass_turn()
            return

        pass_chance = random.randint(0, n_attacks_possibilities)

        if pass_chance == 0:
            self._pass_turn()
            return

        attacker = countries[0]

        enemies = self.player_data['border_countries'][attacker]
        random.shuffle(enemies)

        attacked = enemies[0]

        self._attack_with_everything(attacker, attacked)

    def _exploit(self, id: str):
        leafs = self.tree[id]['leafs']

        best_uct = 0
        best_leaf = None

        # Choose the leaf with best uct value
        for leaf in leafs:
            leaf_id = leaf[0]
            leaf_uct = self._uct(id, leaf_id)

            if leaf_uct >= best_uct:
                best_uct = leaf_uct
                best_leaf = leaf

        if best_leaf[1] == 'pass':
            self._pass_turn()
        else:
            attacker = best_leaf[1]
            attacked = best_leaf[2]
            self._attack_with_everything(attacker, attacked)

    def attack(self):
        """
        When start attacking, attack until the end

        Always attack with max dice

        TODO Make it attack only on advantage?
        """
        is_attacking = self._attack_until_end()
        if is_attacking:
            return

        if self.searching_state == 'exploiting':
            
            id, is_new_node = self._create_node()

            # If is a leaf node, create more leafs to explore
            if len(self.tree[id]['leafs']) == 0:
                self._explore()
                self._add_to_subtree(id)
                if is_new_node:
                    self.searching_state = 'exploring'
                return

            # If is not a leaf, exploit
            else:
                self._exploit(id)
                self._add_to_subtree(id)
                return

        else:
            self._explore()

    def _backpropagation(self, reward: int):
        subtree_size = len(self.subtree)
        for i in reversed(range(subtree_size)):
            id = self.subtree[i][0]
            if i != 0:
                parent_id = str(int(id) - 1)
                # Adiciona como filho o id do filho mais a ação que fez para chegar nele
                if self.subtree[parent_id][1] == 'pass':
                    self.tree[parent_id]['leafs'].append([id, self.subtree[parent_id][1]])
                else:
                    self.tree[parent_id]['leafs'].append([id, self.subtree[parent_id][1], self.subtree[parent_id][2]])
            self.tree[id]['value'] += reward
            self.tree[id]['n_visits'] += 1

    def win(self):
        self._backpropagation(1)
        self._update_game_tree_file()
        print(self.subtree)
        quit()

    def lose(self):
        self._backpropagation(-1)
        self._update_game_tree_file()
        print(self.subtree)
        quit()

if __name__ == "__main__":
    id = MonteCarlo.read_id(sys.argv)

    agent = MonteCarlo(id)

    agent.play()