from datetime import time, datetime
class Route:
    def __init__(self, gtfsId, shortName):
        self.gtfs_id = gtfsId
        self.short_name = shortName
        self.__departure_times = []

    def add_departure_time(self, departure:time):
        if type(departure) == time:
            self.__departure_times.append(departure)

    def get_departure_times(self):
        return self.__departure_times

