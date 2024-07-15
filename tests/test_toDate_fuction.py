# test_my_module.py
import unittest
from datetime import date
from library.functions import toDate, pagination

class TestFunction(unittest.TestCase):

    def test_toDate(self):
        self.assertEqual(toDate("2024-06-07"), date(2024, 6, 7))
        self.assertEqual(toDate("2000-01-01"), date(2000, 1, 1))
        self.assertEqual(toDate("1999-12-31"), date(1999, 12, 31))

    def test_invalid_date_format(self):
        with self.assertRaises(ValueError):
            toDate("2024/06/07")
        with self.assertRaises(ValueError):
            toDate("07-06-2024")
        with self.assertRaises(ValueError):
            toDate("20240607")
        with self.assertRaises(ValueError):
            toDate("June 7, 2024")
        with self.assertRaises(ValueError):
            toDate("2024.06.07")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            toDate("")

    def test_non_date_string(self):
        with self.assertRaises(ValueError):
            toDate("not-a-date")

    def test_incomplete_date(self):
        with self.assertRaises(ValueError):
            toDate("2024-06")
        with self.assertRaises(ValueError):
            toDate("2024-06-")

    def test_numeric_input(self):
        with self.assertRaises(TypeError):
            toDate(20240607)
