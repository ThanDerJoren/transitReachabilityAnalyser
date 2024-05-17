class Itinerary:
    start_time: float
    duration: float
    number_of_transfers: int
    walk_distance: float
    modes = []
    route_numbers = []

    def __init__(self, startTime, duration, numberOfTransfers, walkDistance, modes, routeNumbers):
        self.start_time = startTime
        self.duration = duration
        self.number_of_transfers = numberOfTransfers
        self.walk_distance = walkDistance
        self.modes = modes.copy()
        self.route_numbers = routeNumbers.copy()

