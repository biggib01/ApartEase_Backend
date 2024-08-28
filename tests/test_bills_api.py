"""Tests for Bill CRUD"""
import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Unit, Bill, Resident
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

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)

            # Load unit data from JSON file
            with open('tests/test_data/unit_data.json') as f:
                unit_data = json.load(f)
                for unit in unit_data:
                    new_unit = Unit(
                        numberOfUnits=unit['numberOfUnits'],
                        prevNumberOfUnits=unit['prevNumberOfUnits'],
                        date=unit['date'],
                        extractionStatus=unit['extractionStatus'],
                        approveStatus=unit['approveStatus'],
                        res_room=unit['res_room']
                    )
                    db.session.add(new_unit)

            # Load resident data from JSON file
            with open('tests/test_data/resident_data.json') as f:
                resident_data = json.load(f)
                for resident in resident_data:
                    new_resident = Resident(
                        name=resident['name'],
                        lineId=resident['lineId'],
                        roomNumber=resident['roomNumber']
                    )
                    db.session.add(new_resident)

            # Load bill data from JSON file
            with open('tests/test_data/bill_data.json') as f:
                bill_data = json.load(f)
                for bill in bill_data:
                    new_bill = Bill(
                        unit_id=bill['unit_id'],
                        amount=bill['amount'],
                        date_created=bill['date_created'],
                        res_room=bill['res_room']
                    )
                    db.session.add(new_bill)

            db.session.commit()

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
        fetch_bill = self.client().get('/bill/list/1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bill.status_code, 200)
        response = fetch_bill.data.decode()
        self.assertIn('Bills', ast.literal_eval(response))

    def test_user_logged_in_user_cannot_get_nonexistent_bill_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bill = self.client().get('/bill/list/100', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bill.status_code, 404)
        response = fetch_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'No bills found for the specified room')

    def test_user_logged_in_user_can_get_bills_by_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bills = self.client().get('/bill/list/room?query=101&page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bills.status_code, 200)
        response = fetch_bills.data.decode()
        self.assertIn('Bills', ast.literal_eval(response))

    def test_user_logged_in_user_cannot_get_bills_by_nonexistent_room(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bills = self.client().get('/bill/list/room?query=999&page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bills.status_code, 404)
        response = fetch_bills.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'No bills found for the specified room')

    def test_user_logged_in_user_can_get_all_bills(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_bills = self.client().get('/bill/list?page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_bills.status_code, 200)
        response = fetch_bills.data.decode()
        self.assertIn('Bills', ast.literal_eval(response))

    def test_user_logged_in_user_can_update_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_bill_data = json.dumps({
            "amount": 1800.50,
            "date_created": "2024-08-15"
        })
        update_bill = self.client().put('/bill/edit/1', data=update_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(update_bill.status_code, 200)
        response = update_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill updated successfully')

    def test_user_logged_in_user_cannot_update_nonexistent_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_bill_data = json.dumps({
            "amount": 1800.50,
            "date_created": "2024-08-15"
        })
        update_bill = self.client().put('/bill/edit/100', data=update_bill_data, content_type="application/json", headers=headers)
        self.assertEqual(update_bill.status_code, 404)
        response = update_bill.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill does not exist')

    def test_user_logged_in_user_can_delete_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
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
            "amount": 1800.50,
            "date_created": "2024-08-15"
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
