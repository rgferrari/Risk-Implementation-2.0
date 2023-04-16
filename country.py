class Country:
    """Represents a country.
    
    Attributes
    ----------
    name : str
        A string containing the name of the country.
    neighbours : list
        A list of Country objects with all the country's neighbours.
    owner : Player
        The Player object of the country's owner.
    n_troops : int
        The number of troops on the country.
    """

    def __init__(self, name: str):
        self.name = name
        self.neighbours = []
        self.owner = None
        self.n_troops = 0

    # Legacy
    def add_neighbours(self, countries : list):
        """Add countries to the neighbours list
        
        Parameters
        ----------
        countries : list
            A list with Country objects to be added to the neighbours list
        """

        self.neighbours += countries