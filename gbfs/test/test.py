import json
import math
import os
import unittest
import time

import gbfs

class PositionTest(unittest.TestCase):
    def test_zero_distance(self):
        point1 = point2 = gbfs.Position(1, 1)
        self.assertEqual(gbfs.haversine(point1, point2), 0)

        point3 = gbfs.Position(point1.lon + 360, point1.lat)
        self.assertAlmostEqual(gbfs.haversine(point1, point3), 0)


    def test_earth_circumference(self):
        point1 = gbfs.Position(0, 0)
        point2 = gbfs.Position(180, 0)
        self.assertEqual(gbfs.haversine(point1, point2), math.pi * 6371)

        point3 = gbfs.Position(0, 90)
        self.assertAlmostEqual(gbfs.haversine(point1, point3),
                               math.pi * 6371 / 2)


class StationCollectionTest(unittest.TestCase):
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

    def test_validity(self):
        self.assertTrue(self.station_collection.valid)
        self.station_collection.last_updated -= self.station_collection.ttl
        self.assertFalse(self.station_collection.valid)

    def test_get_id(self):
        self.assertEqual(self.station_collection.get_id("0").station_id, "0")
        self.assertEqual(self.station_collection.get_id("1").station_id, "1")


class StationTest(unittest.TestCase):
    def setUp(self):
        self.s = gbfs.Station("id", "name", 1.1, 2.2)

    def test_ctor(self):
        self.assertEqual(self.s.station_id, "id")
        self.assertEqual(self.s.name, "name")
        self.assertEqual(self.s.position, gbfs.Position(1.1, 2.2))

    def test_repr(self):
        self.assertEqual(str(self.s), "Station('id', 'name')")
        self.assertEqual(repr(self.s), "Station('id', 'name')")

    def test_optional_missing(self):
        for field_name, field_type in gbfs.Station.OPTIONAL_FIELDS:
            self.assertIsNone(getattr(self.s, field_name))

    def test_rental_method(self):
        methods = ["KEY", "CREDITCARD", "PAYPASS", "APPLEPAY", "ANDROIDPAY",
                   "TRANSITCARD", "ACCOUNTNUMBER", "PHONE"]

        # Check we can set each method individually:
        for method in methods:
            s = gbfs.Station("id", "name", 1.1, 2.2, rental_methods=[method])
            self.assertIn(getattr(gbfs.RentalMethod, method), s.rental_methods)

        # ... or all of them at once:
        s = gbfs.Station("id", "name", 1.1, 2.2, rental_methods=methods)
        self.assertEqual(len(s.rental_methods), len(methods))
        for method in methods:
            self.assertIn(getattr(gbfs.RentalMethod, method), s.rental_methods)

    def test_numeric_capacity(self):
        s = gbfs.Station("id", "name", 1.1, 2.2, capacity="1")
        self.assertEqual(s.capacity, 1)

    def test_extra(self):
        self.assertFalse(hasattr(self.s, "dummy_field"))
        s = gbfs.Station("id", "name", 1.1, 2.2, dummy_field="dummy")
        self.assertEqual(s.dummy_field, "dummy")

    def test_empty_status(self):
        self.assertEqual(self.s.num_bikes_available, -1)
        self.assertEqual(self.s.num_docks_available, -1)
        self.assertEqual(self.s.last_reported, -1)
        self.assertEqual(self.s.age, -1)
        self.assertFalse(self.s.is_installed)
        self.assertFalse(self.s.is_renting)
        self.assertFalse(self.s.is_returning)

    def test_push_status(self):
        self.s.push_status("1", "2", "True", "True", "True", "3")
        self.assertEqual(self.s.num_bikes_available, 1)
        self.assertEqual(self.s.num_docks_available, 2)
        self.assertEqual(self.s.last_reported, 3)
        self.assertTrue(self.s.is_installed)
        self.assertTrue(self.s.is_renting)
        self.assertTrue(self.s.is_returning)

    def test_age(self):
        self.s.last_reported = 0
        self.assertGreater(self.s.age, 0)
        self.assertLessEqual(self.s.age, time.time())
