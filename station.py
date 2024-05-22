import json
import datetime
import requests

from pyrosm import OSM
import osmnx as ox
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
from shapely.geometry import Polygon

from stop import Stop # used in relatedStops
from itinerary import Itinerary
import geopy.distance
class Station:




    def __init__(self, name, related_stops):
        self.name = name
        self.related_stops = related_stops  # pass by value? That's important
        self.mean_lat = 0.0
        self.mean_lon = 0.0
        for stop in self.related_stops:
            self.mean_lat += stop.lat
            self.mean_lon += stop.lon
        self.mean_lat = self.mean_lat / len(self.related_stops)
        self.mean_lon = self.mean_lon / len(self.related_stops)
        self.isochrone: Polygon
        self.max_distance_station_to_stop = None

        self.average_trip_time: float = None
        self.car_driving_time: float = None
        self.travel_time_ratio: float = None
        self.average_number_of_transfers: float = None
        self.average_walk_distance_of_trip: float = None
        self.trip_frequency: float = None
        self.queried_itineraries = []
        self.itineraries_with_permissible_catchment_area = []
        self.selected_itineraries = []

    def get_position(self):
        position = {"lat": self.mean_lat, "lon": self.mean_lon}
        return position

    def query_and_create_transit_itineraries(self, date: str, time: str, start: dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        date = f"\"{date}\""
        time = f"\"{time}\""

        if start is None and end is not None:
            start = self.get_position()
        elif start is not None and end is None:
            end = self.get_position()
        elif start is not None and end is not None:
            print("The current station has to be either start or end.\n This function is not intended to plan a route, which dosen't include the current station")
        else:
            print("It has to be pass one: start or end, otherwise the route will be from 'A to A'")
        plan = f"""
            {{plan(
                date: {date},
                time: {time},
                from: {{ lat: {start["lat"]}, lon: {start["lon"]}}},
                to: {{ lat: {end["lat"]}, lon: {end["lon"]}}},
                transportModes: [{{mode: TRANSIT}}, {{mode: WALK}}]
                numItineraries: 10
                walkReluctance: 3.0
                searchWindow: 3600
                ){{
                    itineraries{{
                        startTime,
                        duration,
                        numberOfTransfers,
                        walkDistance,
                        legs{{
                            from{{name}}
                            to{{name}}
                            distance                            
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
            start_station = "" #it needs to be an empty string. If the shortest route is walking, there will be no start station
            end_station = ""
            distance_to_start_station: float
            distance_from_end_station: float
            first_transit_mode = True
            for item in element["legs"]:
                modes.append(item["mode"])
                if first_transit_mode and item["mode"] != "WALK":
                    start_station = item["from"]["name"]
                    first_transit_mode = False
                if item["mode"] != "WALK":
                    end_station = item["to"]["name"]
                if item["route"] is not None:
                    route_numbers.append(item["route"]["shortName"])
                else:
                    route_numbers.append(item["mode"])
            if element["legs"][0]["mode"] == "WALK":
                distance_to_start_station = element["legs"][0]["distance"]
            else:
                distance_to_start_station = 0
            if element["legs"][-1]["mode"] == "WALK":
                distance_from_end_station = element["legs"][-1]["distance"]
            else:
                distance_from_end_station = 0
            itinerary = Itinerary(
                datetime.datetime.fromtimestamp(element["startTime"]/1000.0),  #Unix timestamp in milliseconds to datetime. /1000.0 beacause of milliseconds
                start_station,
                end_station,
                round(element["duration"]/60), # seconds in minutes
                element["numberOfTransfers"],
                element["walkDistance"],
                distance_to_start_station,
                distance_from_end_station,
                modes,
                route_numbers
            )
            self.queried_itineraries.append(itinerary)

    def query_walk_distance(self, start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        if start is None and end is not None:
            start = self.get_position()
        elif start is not None and end is None:
            end = self.get_position()
        elif start is not None and end is not None:
            print("The current station has to be either start or end.\n This function is not intended to plan a route, which dosen't include the current station")
        else:
            print("It has to be pass one: start or end, otherwise the route will be from 'A to A'")
        plan = f"""
            {{plan(
                from: {{ lat: {start["lat"]}, lon: {start["lon"]}}},
                to: {{ lat: {end["lat"]}, lon: {end["lon"]}}},
                transportModes: [{{mode: WALK}}]
                numItineraries: 1
                ){{
                    itineraries{{
                        walkDistance,
                    }}
                }}
            }}
        """
        queriedPlan = requests.post(url, json={"query": plan})
        queriedPlan = json.loads(queriedPlan.content)
        #sometimes, OTP returns an empty list. to prevent an out of bound exception, it iterates through the list, even the max length is 1
        for itinerary in queriedPlan["data"]["plan"]["itineraries"]:
            return itinerary["walkDistance"]
        #return queriedPlan["data"]["plan"]["itineraries"][0]["walkDistance"]

    def query_and_set_car_driving_time(self, start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        if start is None and end is not None:
            start = self.get_position()
        elif start is not None and end is None:
            end = self.get_position()
        elif start is not None and end is not None:
            print("The current station has to be either start or end.\n This function is not intended to plan a route, which dosen't include the current station")
        else:
            print("It has to be pass one: start or end, otherwise the route will be from 'A to A'")
        plan = f"""
                    {{plan(
                        from: {{ lat: {start["lat"]}, lon: {start["lon"]}}},
                        to: {{ lat: {end["lat"]}, lon: {end["lon"]}}},
                        transportModes: [{{mode: CAR}}]
                        numItineraries: 1
                        ){{
                            itineraries{{
                                duration,
                            }}
                        }}
                    }}
                """
        queriedPlan = requests.post(url, json={"query": plan})
        queriedPlan = json.loads(queriedPlan.content)
        for itinerary in queriedPlan["data"]["plan"]["itineraries"]:
            print(f"car Itinerary:",itinerary["duration"], f"station: {self.name}")
            self.car_driving_time = itinerary["duration"]/60 # seconds in minutes

    def filter_itineraries_with_permissible_catchment_area(self, start_or_end_station, catchment_area = 300):
        if start_or_end_station == "start":
            for itinerary in self.queried_itineraries:
                if itinerary.distance_to_start_station <= catchment_area and self.name == itinerary.end_station: # to make sure, that itinerary ends at this exact station and you don't have to walk the last part
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
        elif start_or_end_station == "end":
            for itinerary in self.queried_itineraries:
                if itinerary.distance_from_end_station <= catchment_area and self.name == itinerary.start_station:
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
        else:
            print("It has to be pass either 'start' or 'end'")

    def filter_shortest_itinerary(self):
        if len(self.itineraries_with_permissible_catchment_area)>0:
            self.selected_itineraries.append(self.itineraries_with_permissible_catchment_area[0])
            for itinerary in self.itineraries_with_permissible_catchment_area:
                if itinerary.duration < self.selected_itineraries[0].duration:
                    self.selected_itineraries[0] = itinerary

            self.average_trip_time = self.selected_itineraries[0].duration
            self.average_number_of_transfers = self.selected_itineraries[0].number_of_transfers
            self.average_walk_distance_of_trip = self.selected_itineraries[0].walk_distance


    def calculate_travel_time_ratio(self, start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        self.query_and_set_car_driving_time(start = start, end=end, url=url)
        if self.average_trip_time is not None and self.car_driving_time is not None:
            self.travel_time_ratio = self.average_trip_time/self.car_driving_time
        else:
            print("either the station is not reachable with public tranpsort or the travel_time_ratio is calculated before the PT Trip time")
    def calculate_linear_distance(self, start:dict = None, end: dict = None):
        if start is None and end is not None:
            start = self.get_position()
        elif start is not None and end is None:
            end = self.get_position()
        elif start is not None and end is not None:
            print(
                "The current station has to be either start or end.\n This function is not intended to plan a route, which dosen't include the current station")
        else:
            print("It has to be pass one: start or end, otherwise the route will be from 'A to A'")
        start_coordiante = (start["lat"], start["lon"])
        end_coordinate = (end["lat"], start["lon"])
        return geopy.distance.geodesic(start_coordiante, end_coordinate).m

    def calculate_max_distance_station_to_stop(self):
        max_distance = 0.0
        for stop in self.related_stops:
            end = {"lat": stop.lat, "lon": stop.lon}
            distance = self.query_walk_distance(end = end)
            if distance is None: #backup, if OTP dosen't calculate a walk distane
                distance = self.calculate_linear_distance(end = end)
            print(self.name, distance)
            if distance > max_distance:
                max_distance = distance
        self.max_distance_station_to_stop = max_distance

    def calculate_isochrone(self, G, radius = 300):
        center_node = ox.nearest_nodes(G, self.mean_lon, self.mean_lat) #TODO müsste ersetzt werden, wenn kein conda
        subgraph = nx.ego_graph(G,center_node, radius = radius, distance = "length")
        node_points = [Point((data["x"], data["y"])) for node, data in subgraph.nodes(data=True)]
        self.isochrone = gpd.GeoSeries(node_points).unary_union.convex_hull