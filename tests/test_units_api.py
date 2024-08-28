"""Tests for Unit CRUD"""
import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Unit
from tests.function_for_test.test_function import headerSetUp

class TestUnitCRUD(unittest.TestCase):
    """Testcase for blueprint for units CRUD"""

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

            role_admin = Roles(name='admin')
            role_user = Roles(name='user')

            db.session.add(role_admin)
            db.session.add(role_user)

            user = Users(username='user', password=generate_password_hash('user', method='sha256'))
            admin = Users(username='admin', password=generate_password_hash('admin', method='sha256'))

            unit1 = Unit(numberOfUnits='1001', prevNumberOfUnits='900', date='2024-08-13', extractionStatus='Succeeded', approveStatus=True, res_room='101')
            unit2 = Unit(numberOfUnits='1100', prevNumberOfUnits='1001', date='2024-09-13', extractionStatus='Succeeded', approveStatus=True, res_room='102')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(unit1)
            db.session.add(unit2)
            db.session.commit()

    def test_user_logged_in_user_can_add_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_unit_data = json.dumps({
            "approveStatus": True,
            "numberOfUnits": "1200",
            "res_room": "103"
        })
        add_unit = self.client().post('/unit/add', data=new_unit_data, content_type="application/json", headers=headers)
        self.assertEqual(add_unit.status_code, 200)
        response = add_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Unit record processed successfully')

    def test_user_logged_in_user_can_get_unit_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_unit = self.client().get('/unit/list/1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_unit.status_code, 200)
        response = fetch_unit.data.decode()
        self.assertIn('Unit', ast.literal_eval(response))

    def test_user_logged_in_user_cannot_get_nonexistent_unit_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_unit = self.client().get('/unit/list/100', content_type="application/json", headers=headers)
        self.assertEqual(fetch_unit.status_code, 404)
        response = fetch_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'The unit does not exist')

    def test_user_logged_in_user_can_get_units_by_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_units = self.client().get('/unit/list/room?query=101&page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_units.status_code, 200)
        response = fetch_units.data.decode()
        self.assertIn('Unit', ast.literal_eval(response))

    def test_user_logged_in_user_cannot_get_units_by_nonexistent_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_units = self.client().get('/unit/list/room?query=999&page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_units.status_code, 404)
        response = fetch_units.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'The record with the room number does not exist')

    def test_user_logged_in_user_can_get_all_units(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_units = self.client().get('/unit/list?page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_units.status_code, 200)
        response = fetch_units.data.decode()
        self.assertIn('Unit', ast.literal_eval(response))

    def test_user_logged_in_user_can_update_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_unit_data = json.dumps({
            "numberOfUnits": "1300",
            "approveStatus": False
        })
        update_unit = self.client().put('/unit/edit/1', data=update_unit_data, content_type="application/json", headers=headers)
        self.assertEqual(update_unit.status_code, 200)
        response = update_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Unit data has been updated')

    def test_user_logged_in_user_cannot_update_nonexistent_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_unit_data = json.dumps({
            "numberOfUnits": "1300",
            "approveStatus": False
        })
        update_unit = self.client().put('/unit/edit/100', data=update_unit_data, content_type="application/json", headers=headers)
        self.assertEqual(update_unit.status_code, 404)
        response = update_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], "There's no unit exists!")

    def test_user_logged_in_user_can_delete_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        delete_unit = self.client().delete('/unit/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_unit.status_code, 200)
        response = delete_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Unit deleted successfully!')

    def test_user_logged_in_user_cannot_delete_nonexistent_unit(self):
        headers = headerSetUp(self, 1, self.user_details)
        delete_unit = self.client().delete('/unit/del/100', content_type="application/json", headers=headers)
        self.assertEqual(delete_unit.status_code, 404)
        response = delete_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Unit does not exist')

    def test_user_without_valid_token_cannot_add_unit(self):
        headers = headerSetUp(self, 0, self.user_details)
        new_unit_data = json.dumps({
            "approveStatus": True,
            "numberOfUnits": "1200",
            "res_room": "103"
        })
        add_unit = self.client().post('/unit/add', data=new_unit_data, content_type="application/json", headers=headers)
        self.assertEqual(add_unit.status_code, 401)
        response = add_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_get_units(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_units = self.client().get('/unit/list', content_type="application/json", headers=headers)
        self.assertEqual(fetch_units.status_code, 401)
        response = fetch_units.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_update_unit(self):
        headers = headerSetUp(self, 0, self.user_details)
        update_unit_data = json.dumps({
            "numberOfUnits": "1300",
            "approveStatus": False
        })
        update_unit = self.client().put('/unit/edit/1', data=update_unit_data, content_type="application/json", headers=headers)
        self.assertEqual(update_unit.status_code, 401)
        response = update_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_delete_unit(self):
        headers = headerSetUp(self, 0, self.user_details)
        delete_unit = self.client().delete('/unit/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_unit.status_code, 401)
        response = delete_unit.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

if __name__ == '__main__':
    unittest.main()
