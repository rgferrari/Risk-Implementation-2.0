from country import Country
import random

class _Control:
    last_m_time = None
    call_count = None
    call_path = None
    data_path = None
    call_data = None
    last_call_data = None

class Player:
    """Represents a player

    Parameters
    ----------
    id : {1, 2}
        The unique id of the player.
    n_new_troops : int
        The number of initial troops the player starts with.
    
    Attributes
    ----------
    data_count : int
        Number of times the json with the player state has been updated.
    id : int
        Player unique identifier.
    countries_owned : list
        A list with Country objects containing all the countries owned by the
        player.
    n_new_troops : int
        The number of troops available for being distribuited along the board
        at the mobilizing state.
    n_total_troops : int
        The number of owned troops disposed on the table.
    state : str
        A string containing the current state of the player, they being:
        waiting, mobilizing, conquering, fortifying, attacking, winner and
        loser.
    connection_matrix : dict
        A matrix that tells if there is a land connection between two owned
        countries.

        E.g.: `connection_matrix['country A']['country B'] = True`
    border_countries : dict
        A dict containing as keys all the owned countries next to enemy
        borders and as values all the neighbours that have border with the key.

        E.g.: `{'owned country A': ['enemy neighbour B', 'enemy neighbour C', ...]}`
    """

    def __init__(self, id, n_new_troops):
        self.data_count = 0
        self.id = id
        self.countries_owned = []
        self.n_new_troops = n_new_troops
        self.n_total_troops = 0
        self.state = None
        self.control = _Control()
        self.connection_matrix = {}
        self.border_countries = {}
    
    def attack(self, n_dice : int, attacker : Country, attacked : Country) -> (bool | None):
        """A method called to perform an attack with an owned country against
        an enemy country.

        Parameters
        ----------
        n_dice : int
            The number of dices you want to use to attack.
        attacker : Country
            A Country object of the owned country that will be used to perform
            the attack.
        attacked : Country
            A Country object of the enemy country that will be attacked.

        Returns
        -------
        bool
            True if the enemy country was conquered
            (enemy country has no more enemy troops left).

            False if the enemy country was not conquered
            (enemy country still has troops on it).
        None
            Returns None and print a message in case of the attack is not valid.
        """

        if attacker.owner == self:
            if attacked.owner != self:
                if attacked in attacker.neighbours:                   
                    attacked_dice = 1 if attacked.n_troops == 1 else 2

                    if attacker.n_troops > 1 and (attacker.n_troops - n_dice) >= 1:
                        attacker_dice_values = random.sample(range(1, 7), n_dice)
                        attacked_dice_values = random.sample(range(1, 7), attacked_dice)

                        attacked_dice_values.sort(reverse=True)
                        attacker_dice_values.sort(reverse=True)

                        for i in range(n_dice):
                            if attacked_dice_values[i] >= attacker_dice_values[i]:
                                attacker.n_troops -= 1
                            else:
                                attacked.n_troops -= 1

                            if i == len(attacked_dice_values) - 1:
                                break

                        if attacked.n_troops == 0:
                            return True

                        return False

                    else:
                        print("Player", self.id, "doesn't have enough troops on", attacker.name, "to attack")
                else:
                    print("Player", self.id, "is trying to attack", attacked.name, "that is not neighbour of", attacker.name)
            else:
                print("Player", self.id, "is trying to attack his own country (", attacked.name,")")
        else:
            print("Player", self.id, "is trying to attack with enemy's country (", attacker.name,")")


    def move_troops(self, n_troops : int, from_country : Country, to_country : Country):
        """A method called to perform an attack with an owned country against\\
        an enemy country.

        Parameters
        ----------
        n_troops : int
            The number of troops you want to move between countries.
        from_country : Country
            A Country object of the owned country where the troops will be
            moved from.
        to_country : Country
            A Country object of the owned country where the troops will be
            moved to.
        """

        if(from_country.owner == self):
            if(to_country.owner == self):
                if(n_troops < from_country.n_troops):
                    to_country.n_troops += n_troops
                    from_country.n_troops -= n_troops
                else:
                    print("Player", self.id, "is trying to move", n_troops, "troops, but has only", from_country.n_troops - 1, "available")
            else:
                print("Player", self.id, "is trying to move troops to enemy's country (", to_country.name, ")")
        else:
            print("Player", self.id, "is trying to move troops from enemy's country (", from_country.name, ")")

    def set_new_troops(self, n_troops : int, country : Country):
        """A method called to perform an attack with an owned country\\
        against an enemy country.

        Parameters
        ----------
        n_troops : int
            The number of new troops you want to dispose on the country.
        from_country : Country
            A Country object of the owned country where the new troops will
            be disposed.
        """
        if(country.owner == self):
            if(n_troops <= self.n_new_troops):
                country.n_troops += n_troops
                self.n_total_troops += n_troops
                self.n_new_troops -= n_troops
            else:
                print("Player", self.id, "is trying to set", n_troops, "troops, but has only", self.n_new_troops)
        else:
            print("Player", self.id, "is trying to set troops in enemy's country (", country.name, ")")

    def pass_turn(self):
        """Does nothing."""
        pass