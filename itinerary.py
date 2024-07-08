class Itinerary:

    def __init__(self, startTime, startStation, endStation, duration, numberOfTransfers, walkDistance, walkTime,distanceToStartStation, distanceFromEndStation, modes, routeNumbers, legs, frequency):
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
        self.frequency = frequency
        self.legs = legs
        #print(startStation, endStation, duration, routeNumbers)

    def calculate_frequency(self, route_collection):
        # duration: 18min
        all_frequencies = []
        for trip in self.legs:
            if trip["mode"] != "WALK": #either walk or a transit mode with frequency
                for route in route_collection:
                    if trip["from"]["stop"]["gtfsId"] == route.related_stop_gtfs_id:
                        if trip["route"]["gtfsId"] == route.gtfs_id:
                            print(route.frequency)
                            all_frequencies.append(route.frequency)
            else:
                all_frequencies.append(0.5) # you can start to walk every half minute
                # the unit of all_frequencies is minutes.
        worst_frequency = all_frequencies[0]
        for frequency in all_frequencies:
            if worst_frequency < frequency:  # frequency: every...minute
                worst_frequency = frequency
        print(worst_frequency)
        return worst_frequency
