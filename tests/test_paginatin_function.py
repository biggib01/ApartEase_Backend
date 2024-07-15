# test_pagination.py
import json
import unittest
from library.functions import pagination

# Load the JSON data
lst = [
            {"name": "John", "surname": "Doe"},
            {"name": "Jane", "surname": "Doe"},
            {"name": "Jim", "surname": "Beam"},
            {"name": "Jack", "surname": "Daniels"},
            {"name": "Johnny", "surname": "Walker"},
            {"name": "Jill", "surname": "Stark"},
            {"name": "Jerry", "surname": "Springer"},
            {"name": "Janet", "surname": "Jackson"},
            {"name": "Joseph", "surname": "Smith"},
            {"name": "Jacob", "surname": "Black"}
        ]

class TestPagination(unittest.TestCase):

    def test_first_page_with_per_page_3(self):
        per_page = 3
        total_pages, items_on_page = pagination(1, lst, per_page)
        self.assertEqual(total_pages, 4)
        self.assertEqual(items_on_page, [
            {"name": "John", "surname": "Doe"},
            {"name": "Jane", "surname": "Doe"},
            {"name": "Jim", "surname": "Beam"}
        ])

    def test_middle_page_with_per_page_3(self):
        per_page = 3
        total_pages, items_on_page = pagination(2, lst, per_page)
        self.assertEqual(total_pages, 4)
        self.assertEqual(items_on_page, [
            {"name": "Jack", "surname": "Daniels"},
            {"name": "Johnny", "surname": "Walker"},
            {"name": "Jill", "surname": "Stark"}
        ])

    def test_last_page_with_per_page_3(self):
        per_page = 3
        total_pages, items_on_page = pagination(4, lst, per_page)
        self.assertEqual(total_pages, 4)
        self.assertEqual(items_on_page, [
            {"name": "Jacob", "surname": "Black"}
        ])

    def test_single_page_with_per_page_5(self):
        small_lst = [
            {"name": "John", "surname": "Doe"},
            {"name": "Jane", "surname": "Doe"}
        ]
        per_page = 5
        total_pages, items_on_page = pagination(1, small_lst, per_page)
        self.assertEqual(total_pages, 1)
        self.assertEqual(items_on_page, [
            {"name": "John", "surname": "Doe"},
            {"name": "Jane", "surname": "Doe"}
        ])

    def test_empty_list_with_per_page_5(self):
        empty_lst = []
        per_page = 5
        total_pages, items_on_page = pagination(1, empty_lst, per_page)
        self.assertEqual(total_pages, 0)
        self.assertEqual(items_on_page, [])

    def test_page_out_of_range_with_per_page_3(self):
        per_page = 3
        total_pages, items_on_page = pagination(5, lst, per_page)
        self.assertEqual(total_pages, 4)
        self.assertEqual(items_on_page, [])