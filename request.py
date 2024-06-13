class Request:
    #TODO how to end the code, if except in try except
    def __init__(self, lat, lon, date, time, search_window, catchment_area, ):
        self.lat = lat
        self.lon = lon
        self.date = date
        self.time = time
        self.search_window = search_window
        self.catchment_area = catchment_area
        self.possible_start_stations = []

    @property
    def lat(self):
        return self.__lat

    @lat.setter
    def lat(self, lat):
        try:
            self.__lat = float(lat)
        except ValueError:
            self.iface.messageBar().pushMessage("The lat text field has to contain only numbers")

    @property
    def lon(self):
        return self.__lon

    @lon.setter
    def lon(self, lon):
        try:
            self.__lon = float(lon)
        except ValueError:
            self.iface.messageBar().pushMessage("The lon text field has to contain only numbers")

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
            self.iface.messageBar().pushMessage("The date has to be given in YYYY-MM-DD")

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

    @property
    def search_window(self):
        return self.__search_window

    @search_window.setter
    def search_window(self, search_window):
        if search_window.isdecimal():
            self.__search_window = int(search_window) #set default to 3600 seconds
        else:
            self.iface.messageBar().pushMessage("The search window text field has to contain only numbers")

    @property
    def catchment_area(self):
        return self.__catchment_area

    @catchment_area.setter
    def catchment_area(self, catchment_area):
        try:
            self.__catchment_area = float(catchment_area)
        except ValueError:
            self.iface.messageBar().pushMessage("The catchment area text field has to contain only numbers")




