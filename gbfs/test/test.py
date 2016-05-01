import json
import math
import os
import unittest
import time

import gbfs

class PositionTests(unittest.TestCase):
    def test_zero_distance(self):
        point1 = point2 = gbfs.Position(1, 1)
        self.assertEqual(gbfs.haversine(point1, point2), 0)

        point3 = gbfs.Position(point1.lon + 2 * math.pi, point1.lat)
        self.assertAlmostEqual(gbfs.haversine(point1, point3), 0)


    def test_earth_circumference(self):
        point1 = gbfs.Position(0, 0)
        point2 = gbfs.Position(math.pi, 0)
        self.assertEqual(gbfs.haversine(point1, point2), math.pi * 6371)

        point3 = gbfs.Position(0, math.pi / 2)
        self.assertAlmostEqual(gbfs.haversine(point1, point3),
                               math.pi * 6371 / 2)

class StationCollectionTests(unittest.TestCase):
    def setUp(self):
        self.stations = [gbfs.Station("0", "First Station", 1.1, 2.2),
                         gbfs.Station("1", "Second Station", 3.3, 4.4)]
        self.station_collection = gbfs.StationCollection(time.time(), 10,
                                                         self.stations)

    def test_length(self):
        self.assertEqual(len(self.station_collection), len(self.stations))

    def test_getitem(self):
        for station in self.station_collection:
            self.assertTrue(station.station_id)
            self.assertTrue(station.name)
            self.assertTrue(station.position)
        with self.assertRaises(IndexError):
            self.station_collection[len(self.stations) + 1]

    def test_distances(self):
        all_stations = self.station_collection.near(self.stations[0].position)
        self.assertEqual(len(all_stations), len(self.stations))
        self.assertEqual(all_stations[0][1], 0)
        self.assertGreater(all_stations[1][1], 0)
        self.assertEqual(len(self.station_collection.near(
                             self.stations[0].position, 0)), 1)

    def test_parse_json(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "station_information.json"), "r") as f:
            j = json.load(f)
        stations = gbfs.StationCollection.from_json(j)
        self.assertEqual(len(stations), 2)
