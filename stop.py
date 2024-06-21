from .route import Route
class Stop:

    def __init__(self, name, gtfsId, lat, lon, vehicleMode, relatedRoutes):
        self.name = name
        self.gtfs_id = gtfsId
        self.lat = lat
        self.lon = lon
        self.vehicle_mode = vehicleMode
        self.related_routes = relatedRoutes.copy()
