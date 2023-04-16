from continent import Continent
from country import Country
import json

class World:
    """Represents the world as a not fully connected graph.

    Parameters
    ----------
    world_definition : str
        A string with a path to a json containing the infos of the world.

    Attributes
    ----------
    continents : list
        A list with objects of the type Continent.
    country_list : list
        A list with objects Country.
    country_dict : dict
        A dict with countries as keys and an object Country as value.
    """
    
    def __init__(self, world_definition: str):
        with open(world_definition, 'r') as f:
            world_dict = json.load(f)

        world_data = self._create_world_data(world_dict)
        self.country_dict, self.country_list, self.continents = world_data

    def _create_world_data(self, world_dict: dict) -> tuple:
        """Create all data structures that describes the world.

        Parameters
        ----------
        world_dict : dict
            A dict containing the world definition as follows:
            ```
            {
                'Continent A':{
                    'countries':{
                        'Country A':[
                            'Neighbour A',
                            'Neighbour B',
                            ...   
                        ],
                        'Country B':[
                            'Neighbour A',
                            'Neighbour B',
                            ...   
                        ],
                        ...
                    },
                    'extra_armies': int(x)
                },
                'Continent B'...
            }
            ```

        Returns
        -------
        tuple
            The following tuple: `(country_dict, country_list, continents)`.    
        """
        country_dict = {}
        country_list = []
        continents = []

        # Create countries and continents
        for continent_name, continent_data in world_dict.items():
            countries = continent_data['countries']
            extra_armies = continent_data['extra_armies']
            continent_countries = []
            for country_name, _ in countries.items():
                country = Country(country_name)
                country_dict[country_name] = country
                country_list.append(country)
                continent_countries.append(country)

            continent = Continent(
                continent_name, 
                continent_countries, 
                extra_armies
                )
            continents.append(continent)

        # TODO Is it really needed this second nested loop to assign neighbours?
        # Assign neighbours to each country
        for continent in continents:
            for country in continent.countries:
                neighbours_names = world_dict[continent.name]['countries'][country.name]
                country.neighbours += [country_dict[neighbour_name] for neighbour_name in neighbours_names]

        return (country_dict, country_list, continents)