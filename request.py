
#how to work with datetimepackage: https://docs.python.org/3/library/datetime.html#
from datetime import time, date, datetime
class Request:
    #TODO how to end the code, if except in try except
    #TODO add max_walking_time as field in GUi and pass walk speed and max_walking_time.
    def __init__(self, lat, lon, day, time_start, time_end, walk_speed, max_walking_time):
        self.__incorrect_input = False
        self.__error_message = ""
        self.lat = lat
        self.lon = lon
        self.day = day
        self.time_start = time_start
        #realistisch gesehen ist time_end die letzte ZEit zum lsofahren
        self.time_end = time_end #TODO ist das die letzte ZEit zum losfahren oder die letzte ZEit zum ankommen?
        self.walk_speed = walk_speed
        self.max_walking_time = max_walking_time
        self.catchment_area = self.calculate_distance(self.walk_speed, self.max_walking_time)
        self.__possible_start_stations = []
        self.quality_category = 500
        search_window = self.calculate_search_window()
        self.search_window = search_window

    #TODO will I use the setter after the construction of an objet again? Then it is not a good idea to do the converting inside the setter

    @property
    def lat(self):
        return self.__lat

    @lat.setter
    def lat(self, lat):
        try:
            self.__lat = float(lat)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The lat text field has to contain only numbers" + "\n"

    @property
    def lon(self):
        return self.__lon

    @lon.setter
    def lon(self, lon):
        try:
            self.__lon = float(lon)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The lon text field has to contain only numbers" + "\n"

    @property
    def day(self):
        return self.__day

    @day.setter
    def day(self, day):
        try:
            self.__day = date.fromisoformat(day)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The date has to be given in YYYY-MM-DD" + "\n"

    @property
    def time_start(self):
        return self.__time_start

    @time_start.setter
    def time_start(self, begin):
        try:
            self.__time_start = time.fromisoformat(begin)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The time_start has to be given in hh:mm" + "\n"


    @property
    def time_end(self):
        return self.__time_end

    @time_end.setter
    def time_end(self, end):
        try:
            self.__time_end = time.fromisoformat(end)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The time_end has to be given in hh:mm" + "\n"


    @property
    def search_window(self):
        return self.__search_window

    @search_window.setter
    def search_window(self, search_window):
        try:
            self.__search_window = int(search_window)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The search window text field has to contain only numbers" + "\n"

    @property
    def walk_speed(self):
        return self.__walk_speed

    @walk_speed.setter
    def walk_speed(self, speed):
        self.__walk_speed = speed

    @property
    def max_walking_time(self):
        return self.__max_walking_time

    @max_walking_time.setter
    def max_walking_time(self, duration):
        self.__max_walking_time = duration


    @property
    def catchment_area(self):
        return self.__catchment_area

    @catchment_area.setter
    def catchment_area(self, catchment_area):
        try:
            self.__catchment_area = float(catchment_area)
        except ValueError:
            self.__incorrect_input = True
            self.__error_message += "The catchment area text field has to contain only numbers" + "\n"

    @property
    def incorrect_input(self):
        return self.__incorrect_input

    @property
    def error_message(self):
        return self.__error_message

    @property
    def quality_category(self):
        return self.__quality_category
    @quality_category.setter
    def quality_category(self, value:float):
        self.__quality_category = value

    def calculate_search_window(self):
        diff = datetime.combine(self.day, self.time_end) - datetime.combine(self.day, self.time_start)
        diff = diff.total_seconds()
        if diff >= 0:
            return diff
        else:
            self.__incorrect_input = True
            self.__error_message += "time_start is later than time_end" + "\n"

    def calculate_distance(self, speed, duration):
        distance = speed*duration
        return distance



    def get_possible_start_stations(self):
        return self.__possible_start_stations

    def add_possible_start_station(self, start_station:str):
        if self.__possible_start_stations.count(start_station) == 0:
            self.__possible_start_stations.append(start_station)
        print(f"possible_start_stations: {self.__possible_start_stations}" )

    def remove_empty_entries_in_possible_start_station(self):
        while "" in self.__possible_start_stations:
            self.__possible_start_stations.remove("")  # because of the declaration of stat_station, there can be empty strings in possible_start_station

    def get_letter_of_quality_category(self):
        """
        something like
        0<x<1 = A
        1<=x<1,5 = B
        so I want to change from values to letters at this point
        developement example:
        """
        if self.__quality_category == 500:
            return "Z"


