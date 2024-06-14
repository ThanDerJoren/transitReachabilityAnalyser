class Request:
    #TODO how to end the code, if except in try except
    def __init__(self, lat, lon, date, time, search_window, catchment_area, ):
        self.__incorrect_input = False
        self.__error_message = ""
        self.lat = lat
        self.lon = lon
        self.date = date
        self.time = time
        self.search_window = search_window
        self.catchment_area = catchment_area
        self.__possible_start_stations = []
        self.quality_category = 500


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
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        if (len(date) == 10 and
                date[4] == "-" and
                date[7] == "-" and
                date[0:4].isdecimal() and
                date[5:7].isdecimal() and
                date[8:10].isdecimal() and
                int(date[5:7]) <13 and
                int(date[8:10])<32):
            self.__date = date
        else:
            self.__incorrect_input = True
            self.__error_message += "The date has to be given in YYYY-MM-DD" + "\n"

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, time):
        if (len(time)==5 and
                time[0:2].isdecimal() and
                time[3:5].isdecimal() and
                int(time[0:2])<25 and
                int(time[3:5])<60):
            self.__time = time
        else:
            self.__incorrect_input = True
            self.__error_message += "The time has to be given in hh:mm" + "\n"

    @property
    def search_window(self):
        return self.__search_window

    @search_window.setter
    def search_window(self, search_window):
        if search_window.isdecimal():
            self.__search_window = int(search_window) #set default to 3600 seconds
        else:
            self.__incorrect_input = True
            self.__error_message += "The search window text field has to contain only numbers" + "\n"

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


