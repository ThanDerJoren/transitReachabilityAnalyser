"""
/***************************************************************************
 PublicTransitAnalysis
                                 A QGIS plugin
 Using OpenTripPlanner to calculate public transport reachability from a
    starting point to all stops in a GTFS feed.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-05-14
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Julek Weck
        email                : j.weck@tu-braunschweig.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from .route import Route

class Stop:

    def __init__(self, name, gtfsId, lat, lon, vehicleMode, relatedRoutes):
        self.name = name
        self.gtfs_id = gtfsId
        self.lat = lat
        self.lon = lon
        self.vehicle_mode = vehicleMode
        self.related_routes = relatedRoutes.copy()
