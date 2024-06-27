from datetime import time, datetime
from .request import Request
class Route:
    def __init__(self, gtfsId, shortName, stopId):
        self.gtfs_id = gtfsId
        self.short_name = shortName
        self.related_stop_gtfs_id = stopId
        self.__frequency = None
        self.__departure_times = [] #only the departures between poi.time_start to poi.time_end

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, new_frequency):
        self.__frequency = new_frequency

    def add_departure_time(self, departure:time):
        if type(departure) == time:
            self.__departure_times.append(departure)

    def get_departure_times(self):
        return self.__departure_times

    def calculate_frequency(self, poi:Request):
        time_range = poi.search_window/60 #seconds in minutes
        departure_amount = len(self.get_departure_times())
        frequency = time_range/departure_amount # frequency: every ... minute
        return frequency



