import enum
import json
import math
import time

from collections import namedtuple

#import requests

__all__ = ["Position", "haversine", "EARTH_RADIUS"]

EARTH_RADIUS = 6371.0 # km

# Angles measured in radians
Position = namedtuple('Position', ['lon', 'lat'])

def haversine(pos1, pos2):
    # https://en.wikipedia.org/wiki/Haversine_formula
    delta_lat = pos2.lat - pos1.lat
    delta_lon = pos2.lon - pos1.lon

    return EARTH_RADIUS * 2 * math.asin(math.sqrt(math.sin(delta_lat/2)**2
                                                  + math.cos(pos1.lat)
                                                  * math.cos(pos2.lat)
                                                  * math.sin(delta_lon/2)**2))

