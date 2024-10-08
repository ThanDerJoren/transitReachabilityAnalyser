"""
/***************************************************************************
 PublicTransitAnalysis
                                 A QGIS plugin
 Using OpenTripPlanner to calculate public transport reachability from a
    starting point to all stops in a GTFS feed.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-14
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Julek Weck
        email                : j.weck@tu-braunschweig.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import requests
from datetime import timedelta, datetime

from .stop import Stop # Don't delete! Used in relatedStops
from .itinerary import Itinerary
from .referencePoint import ReferencePoint
import geopy.distance
class Station:
    """
    Every station object combines all Stop objects with the same name.
    The position of the station object is set through the mean of the lat and lon of the related stop objects
    """
    def __init__(self, name, related_stops):
        self.name = name
        self.related_stops = related_stops.copy()
        self.mean_lat = 0.0
        self.mean_lon = 0.0
        for stop in self.related_stops:
            self.mean_lat += stop.lat
            self.mean_lon += stop.lon
        self.mean_lat = self.mean_lat / len(self.related_stops)
        self.mean_lon = self.mean_lon / len(self.related_stops)
        self.max_distance_station_to_stop = None

        self.trip_time: float = None
        self.travel_time_ratio: float = None
        self.itinerary_frequency: float = None
        self.meters_to_first_stop: float = None
        self.number_of_transfers: float = None
        self.car_driving_time: float = None

        self.queried_itineraries = []
        self.itineraries_with_permissible_catchment_area = []
        self.selected_itineraries = []

    def get_position(self):
        position = {"lat": self.mean_lat, "lon": self.mean_lon}
        return position

    def query_transit_itineraries(self, analysis_parameters: ReferencePoint, start_or_end_station, url):
        # query Itineraries
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
        queriedPlan = requests.post(url, json={"query": plan})
        queriedPlan = json.loads(queriedPlan.content)
        itineraries = queriedPlan["data"]["plan"]["itineraries"]
        return itineraries
    def create_transit_itinerary_objects(self, itinerary_collection):
        for element in itinerary_collection:
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
                #The route of a WALK leg is None, so the 'number' is set to WALK
                if item["route"] is not None:
                    route_numbers.append(item["route"]["shortName"])
                else:
                    route_numbers.append(item["mode"])
                #frequency of every leg
                if item["nextLegs"] is not None:
                    if len(item["nextLegs"]) > 2:
                        first_departure = datetime.fromtimestamp(item["startTime"]/1000.0)  #Unix timestamp in milliseconds to datetime. /1000.0 beacause of milliseconds
                        next_legs = item["nextLegs"]
                        average_frequency = self.calculate_average_frequency(first_departure,next_legs)
                        all_frequencies.append(average_frequency)

                    else: #in case there is less then 3 next legs
                        first_departure = datetime.fromtimestamp(item["startTime"] / 1000.0)
                        next_departure = datetime.fromtimestamp(item["nextLegs"][0]["startTime"] / 1000.0)
                        frequency = next_departure - first_departure
                        frequency = round(frequency.total_seconds() / 60, 1)
                        all_frequencies.append(frequency)
                elif item["mode"] == "WALK":
                    all_frequencies.append(0.5)  # you can start to walk every half minute
                else:
                    all_frequencies.append(720) # transit, with no next leg, maybe the last of the day

            # worst frequency of the legs defines the frequency of the whole itinerary
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

    def query_walk_distance(self, url, start:dict = None, end: dict = None):
        # this method can calculate walkdistances to or from this station.
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

    def query_and_set_car_driving_time(self, analysis_parameters:ReferencePoint, start_or_end_station, url):#start:dict = None, end: dict = None, url ="http://localhost:8080/otp/gtfs/v1"):
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
            #An additional 5 minutes will be added for the time needed to prepare the car and for travel delays due to heavy traffic.
            self.car_driving_time = itinerary["duration"]/60 + 5 #seconds in minutes

    def filter_itineraries_with_permissible_catchment_area(self, start_or_end_station, catchment_area):
        if start_or_end_station == "start":
            for itinerary in self.queried_itineraries:
                if len(itinerary.modes) == 1 and itinerary.modes[0] == "WALK" and itinerary.meters_first_stop <= catchment_area:
                    #to ensure, that the possible start stations also are reachable. The next if statement would rule out an only walk itinerary
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
                #the following behavior has to be changed if the end point aren't Stations anymore
                #   then it doesn't make sense anymore to check if the endpoint has the same name as the last stop
                if itinerary.meters_first_stop <= catchment_area and self.name == itinerary.last_stop: # to make sure, that itinerary ends at this exact station and you don't have to walk the last part
                    self.itineraries_with_permissible_catchment_area.append(itinerary)

        elif start_or_end_station == "end":
            # right now, this will never be in use
            for itinerary in self.queried_itineraries:
                if len(itinerary.modes) == 1 and itinerary.modes[0] == "WALK" and itinerary.meters_first_stop <= catchment_area:
                    #to ensure, that the possible start stations also are reachable. The next if statement would rule out an only walk itinerary
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
                if itinerary.meters_end_stop <= catchment_area and self.name == itinerary.first_stop:
                    self.itineraries_with_permissible_catchment_area.append(itinerary)
        else:
            print("It has to be pass either 'start' or 'end'")

    def filter_fastest_itinerary(self):
        if len(self.itineraries_with_permissible_catchment_area)>0:
            self.selected_itineraries.append(self.itineraries_with_permissible_catchment_area[0])
            for itinerary in self.itineraries_with_permissible_catchment_area:
                if itinerary.duration < self.selected_itineraries[0].duration:
                    self.selected_itineraries[0] = itinerary
    def calculate_linear_distance(self, start:dict = None, end: dict = None):
        #this is a backup if OTP can't calculate a walk distance to one point.
        #this can happen if the point is not reachable inside the node-edge model of the street network
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

    def calculate_max_distance_station_to_stop(self, url):
        max_distance = 0.0
        for stop in self.related_stops:
            end = {"lat": stop.lat, "lon": stop.lon}
            distance = self.query_walk_distance(url, end = end)
            if distance is None: #backup, if OTP dosen't calculate a walk distane
                distance = self.calculate_linear_distance(end = end)
            if distance > max_distance:
                max_distance = distance
        self.max_distance_station_to_stop = max_distance

    def calculate_average_frequency(self, first_departure, next_legs:list):
        # two different ways to calculate the mean frequency of a trip
        leg_departure_a = datetime.fromtimestamp(next_legs[1]["startTime"]/1000.0)
        leg_departure_b = datetime.fromtimestamp(next_legs[2]["startTime"]/1000.0)

        diff_departure_a = leg_departure_a - first_departure
        diff_departure_b = leg_departure_b - first_departure

        average_frequency_a = diff_departure_a/2
        average_frequency_b = diff_departure_b/3

        # the longer frequency comes closer to the real frequency. This gets chosen
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

    def set_indicators_of_itinerary(self, analysis_parameters:ReferencePoint, start_or_end_station, url):
        #when the final itinerary is selected, the station attributes regarding the quality of the itinerary can be set
        if self.selected_itineraries != []:
            self.trip_time = self.selected_itineraries[0].duration
            self.number_of_transfers = self.selected_itineraries[0].number_of_transfers
            self.meters_to_first_stop = self.selected_itineraries[0].meters_first_stop
            self.itinerary_frequency = self.selected_itineraries[0].frequency
            self.query_and_set_car_driving_time(analysis_parameters, start_or_end_station, url=url)
            # travel time ratio (TRANSIT/CAR) is calculated only for the selected itinerary, not for all
            if self.trip_time is not None and self.car_driving_time is not None:
                self.travel_time_ratio = self.trip_time / self.car_driving_time




