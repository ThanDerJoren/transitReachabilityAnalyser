import json
import datetime
import requests

#from pyrosm import OSM
#import osmnx as ox
#import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
from shapely.geometry import Polygon

from .stop import Stop # used in relatedStops
from .itinerary import Itinerary
class Station:
    name: str
    mean_lat: float = 0.0
    mean_lon: float = 0.0
    related_stops = []
    isochrone: Polygon

    average_trip_time: float = None
    car_driving_time: float = None
    travel_time_ratio: float = None
    average_number_of_transfers: float = None
    average_walk_distance_of_trip: float = None
    trip_frequency: float = None
    car_itinerary: Itinerary
    possible_itineraries = []
    filtered_itineraries = []

    def __init__(self, name, related_stops):
        self.name = name
        self.related_stops = related_stops  # pass by value? That's important
        for stop in self.related_stops:
            self.mean_lat += stop.lat
            self.mean_lon += stop.lon
        self.mean_lat = self.mean_lat / len(self.related_stops)
        self.mean_lon = self.mean_lon / len(self.related_stops)

    def get_position(self):
        position = {"lat": self.mean_lat, "lon": self.mean_lon}
        return position

    def query_transit_itineraries(self, date: str, time: str, start: dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        date = f"\"{date}\""
        time = f"\"{time}\""

        if start is None and end is not None:
            start = self.get_position()
        elif start is not None and end is None:
            end = self.get_position()
        elif start is not None and end is not None:
            print("The current station has to be either start ot end.\n This function is not intended to plan a route, which dosen't include the current station")
        else:
            print("It has to be pass one: start or end, otherwise the route will be from 'A to A'")

        plan = f"""
            {{plan(
                date: {date},
                time: {time},
                from: {{ lat: {start["lat"]}, lon: {start["lon"]}}},
                to: {{ lat: {end["lat"]}, lon: {end["lon"]}}},
                transportModes: [{{mode: TRANSIT}}, {{mode: WALK}}]
                ){{
                    itineraries{{
                        startTime,
                        duration,
                        numberOfTransfers,
                        walkDistance,
                        legs{{
                            mode
                            route{{shortName}}
                        }}       
                    }}
                }}
            }}
        """
        queriedPlan = requests.post(url, json={"query": plan})
        queriedPlan = json.loads(queriedPlan.content)
        itineraries = queriedPlan["data"]["plan"]["itineraries"]

        for element in itineraries:
            modes = []
            route_numbers = []
            for item in element["legs"]:
                modes.append(item["mode"])
                if item["route"] is not None:
                    route_numbers.append(item["route"]["shortName"])
                else:
                    route_numbers.append(item["route"])

            itinerary = Itinerary(
                datetime.datetime.fromtimestamp(element["startTime"]/1000.0),  #Unix timestamp in milliseconds to datetime. /1000.0 beacause of milliseconds
                round(element["duration"]/60), # seconds in minutes
                element["numberOfTransfers"],
                element["walkDistance"],
                modes,
                route_numbers
            )
            self.possible_itineraries.append(itinerary)
        print(f"{self.name}: all itineraries added.")


    def filter_shortest_itinerary(self):  #ATTENTION: Only for developement purpose
        self.filtered_itineraries.clear()
        self.filtered_itineraries.append(self.possible_itineraries[0])
        for itinerary in self.possible_itineraries:
            if itinerary.duration < self.filtered_itineraries[0].duration:
                self.filtered_itineraries[0] = itinerary

        self.average_trip_time = self.filtered_itineraries[0].duration
        self.average_number_of_transfers = self.filtered_itineraries[0].number_of_transfers
        self.average_walk_distance_of_trip = self.filtered_itineraries[0].walk_distance

    # this method is in comment, because i can't use the packages in QGis right now
    # def calculate_isochrone(self, G, radius = 300):
    #     center_node = ox.nearest_nodes(G, self.mean_lon, self.mean_lat)
    #     subgraph = nx.ego_graph(G,center_node, radius = radius, distance = "length")
    #     node_points = [Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)]
    #     self.isochrone = gpd.GeoSeries(node_points).unary_union.convex_hull