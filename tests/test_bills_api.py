"""Tests for Bill CRUD"""
import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Unit, Resident, Bill
from tests.function_for_test.test_function import headerSetUp

class TestBillCRUD(unittest.TestCase):
    """Testcase for blueprint for bills CRUD"""

    def setUp(self):
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client
        self.user_details = json.dumps({
            'password': 'user',
            'username': 'user'
        })

        # Push an application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

            role_admin = Roles(name='admin')
            role_user = Roles(name='user')

            db.session.add(role_admin)
            db.session.add(role_user)

            user = Users(username='user', password=generate_password_hash('user', method='pbkdf2:sha256'))
            admin = Users(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'))

            unit1 = Unit(numberOfUnits='1001', prevNumberOfUnits='900', date='2024-08-13', extractionStatus='Succeeded', approveStatus=True, res_room='101')
            unit2 = Unit(numberOfUnits='1100', prevNumberOfUnits='1001', date='2024-09-13', extractionStatus='Succeeded', approveStatus=True, res_room='102')

            res1 = Resident(name='supachok jrirarojkul', lineId='line1', roomNumber='101')
            res2 = Resident(name='puwadee pleumpiti', lineId='line2', roomNumber='102')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(res1)
            db.session.add(res2)
            db.session.add(unit1)
            db.session.add(unit2)
            db.session.commit()

    def tearDown(self):
        # Pop the application context
        self.app_context.pop()

    def test_user_logged_in_user_can_add_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        add_bill = self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(add_bill.status_code, 200)
        response = add_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'New bill created')

    def test_user_logged_in_user_can_get_bill_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        fetch_bill = self.client().get('/bill/list/1', content_type="application/json", headers=headers)

        self.assertEqual(fetch_bill.status_code, 200)

        expected_result = {
            'Bill':
            {
                'id': 1,
                'unit_id': 1,
                'amount': 1500.75,
                'date_created': 'Tue, 13 Aug 2024 00:00:00 GMT',  # Update the expected date format
                'res_room': '101'
            }
        }

        response = fetch_bill.get_json()

        self.assertEqual(response, expected_result)

    def test_user_logged_in_user_cannot_get_nonexistent_bill_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bill = self.client().get('/bill/list/100', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bill.status_code, 404)
        response = fetch_bill.get_json()  # Use get_json() to parse the response
        self.assertEqual(response['message'], 'Bill does not exist')


    def test_user_logged_in_user_can_get_bills_by_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        fetch_bills = self.client().get('/bill/list/room?query=101&page=1', content_type="application/json", headers=headers)

        self.assertEqual(fetch_bills.status_code, 200)

        expected_result = {
            "Bills": [
                {
                    "id": 1,
                    "unit_id": 1,
                    "amount": 1500.75,
                    "date_created": "Tue, 13 Aug 2024 00:00:00 GMT",  # Update the expected date format
                    "res_room": "101"
                }
            ],
            "total_pages": 1,
            "page": 1,
            "total_bills": 1
        }

        response = fetch_bills.get_json()

        self.assertEqual(response, expected_result)
    def test_user_logged_in_user_cannot_get_bills_by_nonexistent_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bills = self.client().get('/bill/list/room?query=999&page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bills.status_code, 404)
        response = fetch_bills.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'No bills found for the specified room')



    def test_user_logged_in_user_can_update_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        update_bill_data = json.dumps({
            "amount": 1600.75
        })
        update_bill = self.client().put('/bill/edit/1', data=update_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(update_bill.status_code, 200)
        response = update_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill updated successfully')

    def test_user_logged_in_user_cannot_update_nonexistent_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_bill_data = json.dumps({
            "amount": 1600.75
        })
        update_bill = self.client().put('/bill/edit/100', data=update_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(update_bill.status_code, 404)
        response = update_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill does not exist')

    def test_user_logged_in_user_can_delete_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        delete_bill = self.client().delete('/bill/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_bill.status_code, 200)
        response = delete_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill deleted')

    def test_user_logged_in_user_cannot_delete_nonexistent_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        delete_bill = self.client().delete('/bill/del/100', content_type="application/json", headers=headers)
        self.assertEqual(delete_bill.status_code, 404)
        response = delete_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill does not exist')

    def test_user_without_valid_token_cannot_add_bill(self):
        headers = headerSetUp(self, 0, self.user_details)
        new_bill_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_created": "2024-08-13"
        })
        add_bill = self.client().post('/bill/add/1', data=new_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(add_bill.status_code, 401)
        response = add_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_get_bills(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_bills = self.client().get('/bill/list', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bills.status_code, 401)
        response = fetch_bills.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_update_bill(self):
        headers = headerSetUp(self, 0, self.user_details)
        update_bill_data = json.dumps({
            "amount": 1600.75
        })
        update_bill = self.client().put('/bill/edit/1', data=update_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(update_bill.status_code, 401)
        response = update_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_delete_bill(self):
        headers = headerSetUp(self, 0, self.user_details)
        delete_bill = self.client().delete('/bill/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_bill.status_code, 401)
        response = delete_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

if __name__ == '__main__':
    unittest.main()
