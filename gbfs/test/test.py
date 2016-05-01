import json
import math
import os
import unittest

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

#class StationCollectionTests(unittest.TestCase):
#    def setUp(self):
#        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "station_information.json"), "r") as f:
#            self.json = json.load(f)