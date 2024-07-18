import json
#import datetime
import requests

#from pyrosm import OSM
#import osmnx as ox
#import geopandas as gpd
#import networkx as nx
from shapely.geometry import Point
from shapely.geometry import Polygon
from datetime import timedelta, datetime

from .stop import Stop # used in relatedStops
from .itinerary import Itinerary
from .referencePoint import ReferencePoint
import geopy.distance # TODO find an alternative, which is already installed in qgis python
class Station:




    def __init__(self, name, related_stops):
        self.name = name
        self.related_stops = related_stops.copy()  # pass by value? That's important
        self.mean_lat = 0.0
        self.mean_lon = 0.0
        for stop in self.related_stops:
            self.mean_lat += stop.lat
            self.mean_lon += stop.lon
        self.mean_lat = self.mean_lat / len(self.related_stops)
        self.mean_lon = self.mean_lon / len(self.related_stops)
        self.isochrone: Polygon
        self.max_distance_station_to_stop = None

        self.trip_time: float = None
        self.car_driving_time: float = None
        self.travel_time_ratio: float = None
        self.number_of_transfers: float = None
        self.meters_to_first_stop: float = None
        self.itinerary_frequency: float = None
        self.queried_itineraries = []
        self.itineraries_with_permissible_catchment_area = []
        self.selected_itineraries = []

    def get_position(self):
        position = {"lat": self.mean_lat, "lon": self.mean_lon}
        return position

    def query_and_create_transit_itineraries(self, analysis_parameters: ReferencePoint, start_or_end_station, route_collection,url ="http://localhost:8080/otp/gtfs/v1"): #date: str, time: str, search_window: int, start: dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        day = f"\"{analysis_parameters.day.isoformat()}\""
        departure = f"\"{analysis_parameters.time_start.isoformat(timespec='minutes')}\""

        if start_or_end_station == "start":
            start = {"lat": analysis_parameters.lat, "lon": analysis_parameters.lon}
            end = self.get_position()
        elif start_or_end_station == "end":
            start = self.get_position()
            end = {"lat": analysis_parameters.lat, "lon": analysis_parameters.lon}
        else:
            print("the passed value for start_or_end_station has to be either 'start' or 'end' ")
            return
        #TODO find a good walk reluctance, so more stations are reachable
        plan = f"""
            {{plan(
                date: {day},
                time: {departure},
                from: {{ lat: {start["lat"]}, lon: {start["lon"]}}},
                to: {{ lat: {end["lat"]}, lon: {end["lon"]}}},
                transportModes: [{{mode: TRANSIT}}, {{mode: WALK}}]
                numItineraries: 10
                walkReluctance: 5.0
                searchWindow: {analysis_parameters.search_window}
                walkSpeed: {analysis_parameters.walk_speed}
                ){{
                    itineraries{{
                        startTime,
                        duration,
                        numberOfTransfers,
                        walkDistance,
                        legs{{
                            startTime
                            nextLegs(numberOfLegs:3){{startTime}}
                            mode
                            distance                            
                            from{{ 
                                name
                                stop{{gtfsId}}
                                }}
                            to{{name
                                stop{{gtfsId}}
                                }}
                            route{{
                                shortName
                                gtfsId
                                }}
                        }}       
                    }}
                }}
            }}
        """
        time_query_itineraries = datetime.now()
        queriedPlan = requests.post(url, json={"query": plan})
        queriedPlan = json.loads(queriedPlan.content)
        itineraries = queriedPlan["data"]["plan"]["itineraries"]
        print('         otp_query: {}'.format(datetime.now() - time_query_itineraries))
        num_itineraries = len(itineraries)
        time_create_itineraries = datetime.now()
        for element in itineraries:
            modes = []
            route_numbers = []
            legs = []
            first_stop = "" #it needs to be an empty string. If the shortest route is walking, there will be no start station
            last_stop = ""
            distance_to_first_stop: float
            distance_from_last_stop: float
            first_transit_mode = True
            all_frequencies = []
            for item in element["legs"]:
                legs.append(item)
                modes.append(item["mode"])
                if first_transit_mode and item["mode"] != "WALK":
                    first_stop = item["from"]["name"]
                    first_transit_mode = False
                if item["mode"] != "WALK":
                    last_stop = item["to"]["name"]
                if item["route"] is not None:
                    route_numbers.append(item["route"]["shortName"])
                else:
                    route_numbers.append(item["mode"])

                if item["nextLegs"] is not None:
                    first_departure = datetime.fromtimestamp(item["startTime"]/1000.0)  #Unix timestamp in milliseconds to datetime. /1000.0 beacause of milliseconds
                    next_legs = item["nextLegs"]
                    average_frequency = self.calculate_average_frequency(first_departure,next_legs)
                    all_frequencies.append(average_frequency)
                else:
                    all_frequencies.append(0.5)  # you can start to walk every half minute
            worst_frequency = all_frequencies[0]
            for frequency in all_frequencies:
                if worst_frequency < frequency:  # frequency: every...minute
                    worst_frequency = frequency
            if element["legs"][0]["mode"] == "WALK":
                distance_to_first_stop = element["legs"][0]["distance"]
            else:
                distance_to_first_stop = 0
            if element["legs"][-1]["mode"] == "WALK":
                distance_from_last_stop = element["legs"][-1]["distance"]
            else:
                distance_from_last_stop = 0
            itinerary = Itinerary(
                datetime.fromtimestamp(element["startTime"]/1000.0),  #Unix timestamp in milliseconds to datetime. /1000.0 beacause of milliseconds
                first_stop,
                last_stop,
                round(element["duration"]/60), # seconds in minutes
                element["numberOfTransfers"],
                element["walkDistance"],
                distance_to_first_stop,
                distance_from_last_stop,
                modes,
                route_numbers,
                legs.copy(),
                worst_frequency
            )
            self.queried_itineraries.append(itinerary)
        runtime_loop = datetime.now() - time_create_itineraries
        print('         create itineraries: {}'.format(runtime_loop))
        print(f'        num Itineraries: {num_itineraries}')
        print(f'        average time per itinerary: {runtime_loop}')

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

    def query_and_set_car_driving_time(self, analysis_parameters:ReferencePoint, start_or_end_station, url ="http://localhost:8080/otp/gtfs/v1"):#start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        if start_or_end_station == "start":
            start = {"lat": analysis_parameters.lat, "lon": analysis_parameters.lon}
            end = self.get_position()
        elif start_or_end_station == "end":
            start = self.get_position()
            end = {"lat": analysis_parameters.lat, "lon": analysis_parameters.lon}
        else:
            print("the passed value for start_or_end_station has to be either 'start' or 'end' ")
            return

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
            self.car_driving_time = itinerary["duration"]/60 + 5# seconds in minutes TODO 5 minutes for walking to car and search time

    def filter_itineraries_with_permissible_catchment_area(self, start_or_end_station, catchment_area):
        # TODO check if this new if-statement works
        # the allowed walk distance is used over the whole trip
        # if start_or_end_station =="start":
        #     for itinerary in self.queried_itineraries:
        #         if itinerary.walk_distance <= catchment_area:
        #             self.itineraries_with_permissible_catchment_area.append(itinerary)

        # the allowed walk distance is ony used for the first walk distance
        if start_or_end_station == "start":
            for itinerary in self.queried_itineraries:
                if len(itinerary.modes) == 1 and itinerary.modes[0] == "WALK" and itinerary.meters_first_stop <= catchment_area:
                    #to ensure, that the possible start stations also are reachable. The next if statement would rule out an only walk itinerary
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
                #TODO this behavior has to be changed if the end point aren't Stations anymore
                #   then it doesn't make sense anymore to check if the enpoint has the same name as the last stop
                if itinerary.meters_first_stop <= catchment_area and self.name == itinerary.last_stop: # to make sure, that itinerary ends at this exact station and you don't have to walk the last part
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
        elif start_or_end_station == "end":
            for itinerary in self.queried_itineraries:
                if len(itinerary.modes) == 1 and itinerary.modes[0] == "WALK" and itinerary.meters_first_stop <= catchment_area:
                    #to ensure, that the possible start stations also are reachable. The next if statement would rule out an only walk itinerary
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
                if itinerary.meters_end_stop <= catchment_area and self.name == itinerary.first_stop:
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
        else:
            print("It has to be pass either 'start' or 'end'")

    def filter_shortest_itinerary(self):
        if len(self.itineraries_with_permissible_catchment_area)>0:
            self.selected_itineraries.append(self.itineraries_with_permissible_catchment_area[0])
            for itinerary in self.itineraries_with_permissible_catchment_area:
                if itinerary.duration < self.selected_itineraries[0].duration:
                    self.selected_itineraries[0] = itinerary

            self.trip_time = self.selected_itineraries[0].duration
            self.number_of_transfers = self.selected_itineraries[0].number_of_transfers
            self.meters_to_first_stop = self.selected_itineraries[0].meters_first_stop
            self.itinerary_frequency = self.selected_itineraries[0].frequency

    def calculate_travel_time_ratio(self, analysis_parameters:ReferencePoint, start_or_end_station, url ="http://localhost:8080/otp/gtfs/v1"): #start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
        self.query_and_set_car_driving_time(analysis_parameters, start_or_end_station, url=url)
        if self.trip_time is not None and self.car_driving_time is not None:
            self.travel_time_ratio = self.trip_time / self.car_driving_time
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
        time_walk_distance_station_stop = datetime.now()
        max_distance = 0.0
        for stop in self.related_stops:
            end = {"lat": stop.lat, "lon": stop.lon}
            distance = self.query_walk_distance(end = end)
            if distance is None: #backup, if OTP dosen't calculate a walk distane
                distance = self.calculate_linear_distance(end = end)
            if distance > max_distance:
                max_distance = distance
        self.max_distance_station_to_stop = max_distance
        print('time_walk_distance_station_stop: {}'.format(datetime.now() - time_walk_distance_station_stop))

    def calculate_average_frequency(self, first_departure, next_legs:list):
        #TODO comment
        leg_departure_a = datetime.fromtimestamp(next_legs[1]["startTime"]/1000.0)
        leg_departure_b = datetime.fromtimestamp(next_legs[2]["startTime"]/1000.0)

        diff_departure_a = leg_departure_a - first_departure
        diff_departure_b = leg_departure_b - first_departure

        average_frequency_a = diff_departure_a/2
        average_frequency_b = diff_departure_b/3

        if average_frequency_a > average_frequency_b:
            average_frequency = average_frequency_a
        else:
            average_frequency = average_frequency_b
        average_frequency = round(average_frequency.total_seconds() / 60, 1)
        return average_frequency




        # runtime: 45min because of for loop
        # one_hour = timedelta(minutes=60)
        # search_window = first_departure + one_hour
        # last_departure = 0
        # num_legs = 0
        # departure_range = 0
        # if datetime.fromtimestamp(next_legs[0]["startTime"]/1000.0)< search_window:
        #     num_legs +=1
        #     #frequency is shorter than 60 min
        #     for leg in next_legs:
        #         leg_departure = datetime.fromtimestamp(leg["startTime"]/1000.0)
        #         print(f"leg_departure: {leg_departure}, {type(leg_departure)}")
        #         if leg_departure < search_window:
        #             num_legs +=1
        #             last_departure = leg_departure #next_legs has to be ordered
        #             departure_range = timedelta(minutes=60)
        #         else:
        #             break
        # elif datetime.fromtimestamp(next_legs[-1]["startTime"]/1000.0) < search_window:
        #     # thats why it has to be 12 nextLegs. 5min frequency -> the 12th departure == first departure +1h
        #     # if the frequency is shorter than 5 min, the 12th departure is < first departure +1h
        #     last_departure = datetime.fromtimestamp(next_legs[-1]["startTime"]/1000.0)
        #     num_legs = 12
        #     departure_range = last_departure - first_departure
        # else:
        #     last_departure = datetime.fromtimestamp(next_legs[0]["startTime"]/1000.0)
        #     num_legs = 1
        #     departure_range = last_departure - first_departure
        # average_frequency = departure_range/(num_legs)
        # average_frequency = round(average_frequency.total_seconds() / 60, 1)
        # return average_frequency




