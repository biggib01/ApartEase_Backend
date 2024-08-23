import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident, Unit
from tests.function_for_test.test_function import headerSetUp

class TestUnitRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client
        self.user_details = json.dumps({
            'password': 'user',
            'username': 'user'
        })

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

            role_user = Roles(name='user')
            db.session.add(role_user)

            user = Users(username='user', password=generate_password_hash('user', method='sha256'))
            user.roles.append(role_user)
            db.session.add(user)
            db.session.commit()

    def test_user_logged_in_user_can_add_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        response = self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn('new record created', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_add_a_unit_with_duplicate_data(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        response = self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Record already exists', response.get_data(as_text=True))

    def test_user_without_valid_token_cannot_add_unit(self):
        headers = headerSetUp(self, 0, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        response = self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.get_data(as_text=True))

    def test_user_logged_in_user_can_get_units_list_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list?page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_user_logged_in_user_cannot_get_units_list_before_having_data_in_DB(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list?page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_get_units_list_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list?page=100', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found', response.get_data(as_text=True))

    def test_user_without_valid_token_cannot_get_units_list(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().get('/unit/list', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.get_data(as_text=True))

    def test_user_logged_in_user_can_get_units_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        response = self.client().get('/unit/list/1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('numberOfUnits', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_get_units_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/100', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Unit does not exist', response.get_data(as_text=True))

    def test_user_without_valid_token_cannot_get_units_by_id(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().get('/unit/list/1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.get_data(as_text=True))

    def test_user_logged_in_user_can_search_units_by_room_number(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        response = self.client().get('/unit/list/room?query=101&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('numberOfUnits', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_search_units_by_non_exist_room_number_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/room?query=999&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found for the given room number', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_search_units_by_room_number_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/room?query=101&page=100', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found', response.get_data(as_text=True))

    def test_user_without_valid_token_cannot_search_units_by_room_number(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().get('/unit/list/room?query=101&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.get_data(as_text=True))

    def test_user_logged_in_user_can_filter_units_by_date_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "approved",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        response = self.client().get('/unit/list/date?start=2024-01-01&end=2024-12-31&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('numberOfUnits', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_filter_units_by_date_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/date?start=2024-01-01&end=2024-12-31&page=100', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found', response.get_data(as_text=True))

    def test_user_logged_in_user_cannot_filter_units_by_non_exist_date_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/date?start=2030-01-01&end=2030-12-31&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No unit data found for the given date range', response.get_data(as_text=True))

    def test_user_logged_in_user_get_a_blank_list_by_filter_units_without_input_date(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/list/date?page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid date range', response.get_data(as_text=True))

    def test_user_without_valid_token_cannot_filter_units_by_date_with_page(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().get('/unit/list/date?start=2024-01-01&end=2024-12-31&page=1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token', response.get_data(as_text=True))

    def test_user_logged_in_user_can_update_all_units_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "approved",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        update_data = json.dumps({
            "numberOfUnits": "2002",
            "date": "2024-07-13",
            "extractionStatus": "pending",
            "approveStatus": True,
            "res_room": "102",
            "costPerUnit": 6.0,
            "waterCost": 12.0,
            "rentCost": 600.0
        })
        response = self.client().put('/unit/edit/1', data=update_data, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Record data has been updated', response.get_data(as_text=True))

    def test_user_logged_in_user_can_update_only_units_numberOfUnits_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        unit_data = json.dumps({
            "numberOfUnits": "1001",
            "date": "2024-06-13",
            "extractionStatus": "2001",
            "approveStatus": False,
            "res_room": "101",
            "costPerUnit": 5.0,
            "waterCost": 10.0,
            "rentCost": 500.0
        })
        self.client().post('/unit/add', data=unit_data, content_type='application/json', headers=headers)
        update_data = json.dumps({
            "numberOfUnits": "2002"
        })
        response = self.client().put('/unit/edit/1', data=update_data, content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Record data has been updated', response.get_data(as_text=True))




if __name__ == '__main__':
    unittest.main()
