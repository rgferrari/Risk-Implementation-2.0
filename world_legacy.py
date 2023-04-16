from continent import Continent
from country import Country
import json

class World:
    """Represents the world as a not fully connected graph

    Attributes
    ----------
    continents : list
        A list with objects of the type Continent
    country_dict : dict
        A dict with countries as keys and an object Country as value
    country_list : list
        A list with objects Country
    """
    
    def __init__(self):
        # Initiate continents
        north_america = Continent("North America")
        south_america = Continent("South America")
        australia = Continent("Australia")
        europe = Continent("Europe")
        asia = Continent("Asia")
        africa = Continent("Africa")

        north_america.extra_armies = 5
        south_america.extra_armies = 2
        australia.extra_armies = 2
        europe.extra_armies = 5
        asia.extra_armies = 7
        africa.extra_armies = 3

        self.continents = [
            north_america,
            south_america,
            australia,
            europe,
            asia,
            africa
        ]

        north_america_countries = [
            "Alaska",
            "Alberta",
            "Ontario",
            "Western America",
            "Eastern America",
            "Quebec",
            "Central America",
            "Greenland",
            "Northwest America"
            ]
        south_america_countries = [
            "Brazil",
            "Venezuela",
            "Peru",
            "Argentina"
            ]
        australia_countries = [
            "Western Australia",
            "Eastern Australia",
            "Indoneasia",
            "Papua New Guinea"
            ]
        europe_countries = [
            "Ukraine",
            "Skandinavia",
            "Iceland",
            "Great Britain",
            "Northern Europe",
            "Western Europe",
            "Southern Europe"
            ]
        asia_countries = [
            "Yakutsk",
            "Siberia",
            "Kamchatka",
            "Irkutsk",
            "Ural",
            "Japan",
            "Mongolia",
            "China",
            "Middle East",
            "India",
            "Siam",
            "Afganistan"
            ]
        africa_countries = [
            "Congo",
            "East Africa",
            "Egypt",
            "Madagascar",
            "North Africa",
            "South Africa"
            ]
        
        _continents_countries = [
            north_america_countries,
            south_america_countries,
            australia_countries,
            europe_countries,
            asia_countries,
            africa_countries
            ] # TODO Maybe this is not necessary

        self.country_dict = {}
        self.country_list = [] # TODO Maybe this is not necessary

        for i, continent_countries in enumerate(_continents_countries):
            for country_name in continent_countries:
                country = Country(country_name)
                self.country_dict[country_name] = country
                self.country_list.append(country)
                self.continents[i].countries.append(country)
        
        # North America
        self.country_dict["Alaska"].add_neighbours([self.country_dict["Northwest America"], self.country_dict["Alberta"], self.country_dict["Kamchatka"]])
        self.country_dict["Alberta"].add_neighbours([self.country_dict["Alaska"], self.country_dict["Ontario"], self.country_dict["Northwest America"], self.country_dict["Western America"]])
        self.country_dict["Ontario"].add_neighbours([self.country_dict["Alberta"], self.country_dict["Quebec"], self.country_dict["Northwest America"], self.country_dict["Eastern America"], self.country_dict["Greenland"], self.country_dict["Western America"]])
        self.country_dict["Northwest America"].add_neighbours([self.country_dict["Alberta"], self.country_dict["Alaska"], self.country_dict["Ontario"], self.country_dict["Greenland"]])
        self.country_dict["Western America"].add_neighbours([self.country_dict["Alberta"], self.country_dict["Ontario"], self.country_dict["Central America"], self.country_dict["Eastern America"]])
        self.country_dict["Eastern America"].add_neighbours([self.country_dict["Ontario"], self.country_dict["Quebec"], self.country_dict["Central America"], self.country_dict["Western America"]])
        self.country_dict["Quebec"].add_neighbours([self.country_dict["Greenland"], self.country_dict["Ontario"], self.country_dict["Eastern America"]])
        self.country_dict["Central America"].add_neighbours([self.country_dict["Eastern America"], self.country_dict["Western America"], self.country_dict["Venezuela"]])
        self.country_dict["Greenland"].add_neighbours([self.country_dict["Ontario"], self.country_dict["Quebec"], self.country_dict["Northwest America"], self.country_dict["Iceland"]])

        # South America
        self.country_dict["Brazil"].add_neighbours([self.country_dict["Venezuela"], self.country_dict["Peru"], self.country_dict["Argentina"], self.country_dict["North Africa"]])
        self.country_dict["Venezuela"].add_neighbours([self.country_dict["Brazil"], self.country_dict["Peru"], self.country_dict["Central America"]])
        self.country_dict["Peru"].add_neighbours([self.country_dict["Brazil"], self.country_dict["Venezuela"], self.country_dict["Argentina"]])
        self.country_dict["Argentina"].add_neighbours([self.country_dict["Peru"], self.country_dict["Brazil"]])

        # Australia
        self.country_dict["Western Australia"].add_neighbours([self.country_dict["Eastern Australia"], self.country_dict["Indoneasia"], self.country_dict["Papua New Guinea"]])
        self.country_dict["Eastern Australia"].add_neighbours([self.country_dict["Papua New Guinea"], self.country_dict["Western Australia"]])
        self.country_dict["Indoneasia"].add_neighbours([self.country_dict["Siam"], self.country_dict["Papua New Guinea"], self.country_dict["Western Australia"]])
        self.country_dict["Papua New Guinea"].add_neighbours([self.country_dict["Indoneasia"], self.country_dict["Eastern Australia"], self.country_dict["Western Australia"]])

        # Europe
        self.country_dict["Ukraine"].add_neighbours([self.country_dict["Skandinavia"], self.country_dict["Northern Europe"], self.country_dict["Southern Europe"], self.country_dict["Middle East"], self.country_dict["Ural"], self.country_dict["Afganistan"]])
        self.country_dict["Skandinavia"].add_neighbours([self.country_dict["Iceland"], self.country_dict["Great Britain"], self.country_dict["Northern Europe"], self.country_dict["Ukraine"]])
        self.country_dict["Iceland"].add_neighbours([self.country_dict["Skandinavia"], self.country_dict["Great Britain"], self.country_dict["Greenland"]])
        self.country_dict["Great Britain"].add_neighbours([self.country_dict["Iceland"], self.country_dict["Skandinavia"], self.country_dict["Northern Europe"], self.country_dict["Western Europe"]])
        self.country_dict["Northern Europe"].add_neighbours([self.country_dict["Great Britain"], self.country_dict["Skandinavia"], self.country_dict["Ukraine"], self.country_dict["Western Europe"], self.country_dict["Southern Europe"]])
        self.country_dict["Western Europe"].add_neighbours([self.country_dict["Great Britain"], self.country_dict["Northern Europe"], self.country_dict["Southern Europe"], self.country_dict["North Africa"]])
        self.country_dict["Southern Europe"].add_neighbours([self.country_dict["Ukraine"], self.country_dict["Middle East"], self.country_dict["Egypt"], self.country_dict["North Africa"], self.country_dict["Western Europe"], self.country_dict["Northern Europe"]])

        # Asia
        self.country_dict["Yakutsk"].add_neighbours([self.country_dict["Siberia"], self.country_dict["Irkutsk"], self.country_dict["Kamchatka"]])
        self.country_dict["Siberia"].add_neighbours([self.country_dict["Yakutsk"], self.country_dict["Irkutsk"], self.country_dict["Mongolia"], self.country_dict["China"], self.country_dict["Ural"]])
        self.country_dict["Kamchatka"].add_neighbours([self.country_dict["Yakutsk"], self.country_dict["Irkutsk"], self.country_dict["Japan"], self.country_dict["Mongolia"], self.country_dict["Alaska"]])
        self.country_dict["Irkutsk"].add_neighbours([self.country_dict["Siberia"], self.country_dict["Kamchatka"], self.country_dict["Yakutsk"], self.country_dict["Mongolia"]])
        self.country_dict["Ural"].add_neighbours([self.country_dict["Ukraine"], self.country_dict["Afganistan"], self.country_dict["China"], self.country_dict["Siberia"]])
        self.country_dict["Japan"].add_neighbours([self.country_dict["Kamchatka"], self.country_dict["Mongolia"]])
        self.country_dict["Mongolia"].add_neighbours([self.country_dict["China"], self.country_dict["Siberia"], self.country_dict["Irkutsk"], self.country_dict["Kamchatka"], self.country_dict["Japan"]])
        self.country_dict["China"].add_neighbours([self.country_dict["Afganistan"], self.country_dict["Ural"], self.country_dict["Siberia"], self.country_dict["Mongolia"], self.country_dict["Siam"], self.country_dict["India"]])
        self.country_dict["Middle East"].add_neighbours([self.country_dict["India"], self.country_dict["Afganistan"], self.country_dict["Egypt"], self.country_dict["East Africa"], self.country_dict["Southern Europe"], self.country_dict["Ukraine"]])
        self.country_dict["India"].add_neighbours([self.country_dict["Middle East"], self.country_dict["Afganistan"], self.country_dict["China"], self.country_dict["Siam"]])
        self.country_dict["Siam"].add_neighbours([self.country_dict["China"], self.country_dict["India"], self.country_dict["Indoneasia"]])
        self.country_dict["Afganistan"].add_neighbours([self.country_dict["Ukraine"], self.country_dict["Ural"], self.country_dict["China"], self.country_dict["India"], self.country_dict["Middle East"]])

        # Africa
        self.country_dict["Congo"].add_neighbours([self.country_dict["North Africa"], self.country_dict["East Africa"], self.country_dict["South Africa"]])
        self.country_dict["East Africa"].add_neighbours([self.country_dict["Egypt"], self.country_dict["North Africa"], self.country_dict["Congo"], self.country_dict["South Africa"], self.country_dict["Madagascar"], self.country_dict["Middle East"]])
        self.country_dict["Egypt"].add_neighbours([self.country_dict["North Africa"], self.country_dict["East Africa"], self.country_dict["Southern Europe"], self.country_dict["Middle East"]])
        self.country_dict["Madagascar"].add_neighbours([self.country_dict["South Africa"], self.country_dict["East Africa"]])
        self.country_dict["North Africa"].add_neighbours([self.country_dict["Egypt"], self.country_dict["East Africa"], self.country_dict["Congo"], self.country_dict["Brazil"], self.country_dict["Western Europe"], self.country_dict["Southern Europe"]])
        self.country_dict["South Africa"].add_neighbours([self.country_dict["Congo"], self.country_dict["East Africa"], self.country_dict["Madagascar"]])

if __name__ == '__main__':
    world = World()

    world_as_dict = {}
    for continent in world.continents:
        world_as_dict[continent.name] = {'countries': {}, 'extra_armies': continent.extra_armies}
        for country in continent.countries:
            print(country.name, [neighbour.name for neighbour in country.neighbours])
            world_as_dict[continent.name]['countries'][country.name] = [neighbour.name for neighbour in country.neighbours]

    with open('worlds/classic.json', 'w') as f:
        json.dump(world_as_dict, f)

"""
{
    Continent A:{
        Countries:{
            Country A:[
                Neighbour A,
                Neighbour B,
                ...   
            ],
            Country B:[
                Neighbour A,
                Neighbour B,
                ...   
            ],
            ...
        },
        Bonus Troops: x
    },
    Continent B...
}
"""