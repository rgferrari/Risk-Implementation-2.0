class Continent:
    """Represents a continent.

    Attributes
    ---------
    name : str
        A string containing the continent's name.
    countries : list
        A list of Country objects with all the continent's countries.
    owner : Player
        The Player object of the continent's owner.
    extra_armies : int
        The number of extra armies that the continent provides to its owner at
        the end of the round.
    """

    def __init__(self, name: str, countries: list = None, extra_armies = 0):
        if countries is None:
            countries = []
        self.name = name
        self.countries = countries
        self.owner = None
        self.extra_armies = 0

    def update_continent_owner(self):
        """Iterates over all the countries checking their owners. If all the\\
        countries have the same owner, it becomes the owner of the continent."""

        owner = None
        has_owner = True

        for country in self.countries:
            if owner == None:
                owner = country.owner
            elif owner != country.owner:
                has_owner = False
                break
        
        if has_owner:
            self.owner = owner
        else:
            self.owner = None