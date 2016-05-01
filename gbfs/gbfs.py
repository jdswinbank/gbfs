import enum
import json
import math
import time

from collections import namedtuple

#import requests

__all__ = ["Position", "haversine", "EARTH_RADIUS", "StationCollection",
           "Station"]

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

class StationCollection(object):
    def __init__(self, ttl, last_updated, stations):
        self.ttl = ttl
        self.last_updated = last_updated
        self.stations = list(stations)

    def __getitem__(self, *args, **kwargs):
        return self.stations.__getitem__(*args, **kwargs)

    def __len__(self):
        return len(self.stations)

    def near(self, position, radius=None):
        """
        Find stations near ``position``.

        Returns a list of (station, distance) tuples for all stations within
        ``radius`` km of ``position``, sorted by distance.
        """
        return [(station, haversine(position, station.position))
                for station in self
                if radius is None
                or haversine(position, station.position) <= radius]

    @staticmethod
    def from_json(json):
        """
        Parse GBFS-style JSON and return a StationCollecton.
        """
        ttl = int(json['ttl'])
        last_updated = int(json['last_updated'])
        stations = [Station(**data) for data in json['data']['stations']]
        return StationCollection(ttl, last_updated, stations)

    @property
    def valid(self):
        """
        Return True if the ``last_updated`` time is more recent than the TTL.
        """
        return (time.time() - self.last_updated) <= self.ttl

class Station(object):
    def __init__(self, station_id, name, lon, lat, **kwargs):
        self.station_id = str(station_id)
        self.name = str(name)
        self.position = Position(math.radians(lon), math.radians(lat))

    def __repr__(self):
        return 'Station(%r, %r)' % (self.station_id, self.name)
