import enum
import json
import math
import time

from collections import namedtuple

#import requests

__all__ = ["Position", "haversine", "EARTH_RADIUS", "StationCollection",
           "Station", "RentalMethod"]

EARTH_RADIUS = 6371.0 # km

class RentalMethod(enum.Enum):
    """
    All possible rental methods in standard as of 2016-05-01.
    """
    # This may be gratuitous: additional methods can be added in future, so
    # locking down the enumeration will just cause breakage. Useful for
    # sanity checking for now, though.
    KEY = 0
    CREDITCARD = 1
    PAYPASS = 2
    APPLEPAY = 3
    ANDROIDPAY = 4
    TRANSITCARD = 5
    ACCOUNTNUMBER = 6
    PHONE = 7

# Angles measured in degrees
Position = namedtuple('Position', ['lon', 'lat'])

def haversine(pos1, pos2):
    # https://en.wikipedia.org/wiki/Haversine_formula
    delta_lat = math.radians(pos2.lat - pos1.lat)
    delta_lon = math.radians(pos2.lon - pos1.lon)

    return EARTH_RADIUS * 2 * math.asin(math.sqrt(math.sin(delta_lat/2)**2
                                                  + math.cos(math.radians(pos1.lat))
                                                  * math.cos(math.radians(pos2.lat))
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

    def get_id(self, station_id):
        """
        Return a station with ID ``station_id``, or ``None``.
        """
        # Probably StationCollection should actually be a mapping of
        # station_id -> station. But it's not at the moment.
        for station in self.stations:
            if station.station_id == station_id:
                return station
        return None


class Station(object):
    # Optional fields in the GBFS spec, provided as pairs of (field_name,
    # callable), where callable is used to cast whatever input is provided to
    # an appropriate type.
    OPTIONAL_FIELDS = [("short_name", str),
                       ("address", str),
                       ("cross_street", str),
                       ("region_id", str),
                       ("post_code", str),
                       ("rental_methods", lambda x: {getattr(RentalMethod, y)
                                                     for y in x}),
                       ("capacity", int)]

    def __init__(self, station_id, name, lon, lat, **kwargs):
        self.station_id = str(station_id)
        self.name = str(name)
        self.position = Position(float(lon), float(lat))

        # All optional fields (ie, as defined in the spec) are set to None if
        # they don't exist.
        for field_name, field_type in self.OPTIONAL_FIELDS:
            try:
                value = field_type(kwargs.pop(field_name))
            except KeyError:
                value = None
            setattr(self, field_name, value)

        # Fields which aren't defined in the spec are also saved; this is
        # relevant for e.g. Citibike's eightd_has_key_dispenser.
        for field, value in kwargs.items():
            setattr(self, field, value)

    def __repr__(self):
        return 'Station(%r, %r)' % (self.station_id, self.name)
