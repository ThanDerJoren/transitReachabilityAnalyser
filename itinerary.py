class Itinerary:

    def __init__(self, startTime, startStation, endStation, duration, numberOfTransfers, walkDistance, walkTime,distanceToStartStation, distanceFromEndStation, modes, routeNumbers, legs):
        self.start_time = startTime
        self.start_station = startStation
        self.end_station = endStation
        self.duration = duration
        self.number_of_transfers = numberOfTransfers
        self.walk_distance = walkDistance
        self.walk_time = walkTime
        self.distance_to_start_station = distanceToStartStation
        self.distance_from_end_station = distanceFromEndStation
        self.modes = modes.copy()
        self.route_numbers = routeNumbers.copy()
        self.frequency = None
        self.legs = legs
        #print(startStation, endStation, duration, routeNumbers)

    def calculate_frequency(self, station_collection, poi):
        all_frequencies = []
        print(f"legs: {self.legs}")
        print("number of legs: ",len(self.legs))
        for trip in self.legs:
            if trip["mode"] != "WALK": #either walk or a transit mode with frequency
                for station in station_collection:
                    if trip["from"]["name"] == station.name:
                        for stop in station.related_stops:
                            if trip["from"]["stop"]["gtfsId"] == stop.gtfs_id:
                                for route in stop.related_routes:
                                    if trip["route"]["gtfsId"] == route.gtfs_id:
                                        print(route.frequency)
                                        all_frequencies.append(route.frequency)
                    #                 else:
                    #                     print(f"route ids doesn't match: {trip['route']['gtfsId']} == {route.gtfs_id}")
                    #         else:
                    #             print(f"start stop id doesn't match the stopid: {trip['from']['stop']['gtfsId']} == {stop.gtfs_id}")
                    # else:
                    #     print(f"stop name doesn't match with the station name: {trip['from']['name']} == {station.name}")
            else:
                all_frequencies.append(0.5) # you can start to walk every half minute
                # the unit of all_frequencies is minutes.
        print(f"{self.end_station}, frequency: {all_frequencies}")
        worst_frequency = all_frequencies[0]
        for frequency in all_frequencies:
            if worst_frequency < frequency: #frequency: every...minute
                worst_frequency = frequency
        print(worst_frequency)
        return worst_frequency





