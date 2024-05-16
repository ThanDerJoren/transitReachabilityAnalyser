class Stop:
    name: str
    gtfs_id: str
    lat: float
    lon: float
    vehicle_mode: str

    def __init__(self, name, gtfsId, lat, lon, vehicleMode):
        self.name = name
        self.gtfs_id = gtfsId
        self.lat = lat
        self.lon = lon
        self.vehicle_mode = vehicleMode
