"""Tests for Bill History CRUD"""
import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Unit, Bill, BillHistory, Resident
from tests.function_for_test.test_function import headerSetUp

class TestBillHistoryCRUD(unittest.TestCase):
    """Testcase for blueprint for bill history CRUD"""

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

            user = Users(username='user', password=generate_password_hash('user', method='pbkdf2:sha256'))
            admin = Users(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'))

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
                        date_created=bill['date_created']
                    )
                    db.session.add(new_bill)

            # Load bill history data from JSON file
            with open('tests/test_data/bill_history_data.json') as f:
                bill_history_data = json.load(f)
                for history in bill_history_data:
                    new_history = BillHistory(
                        unit_id=history['unit_id'],
                        amount=history['amount'],
                        date_sent=history['date_sent'],
                        rent_cost=history['rent_cost'],
                        water_cost=history['water_cost'],
                        cost_per_unit=history['cost_per_unit']
                    )
                    db.session.add(new_history)

            db.session.commit()

    def test_user_logged_in_user_can_add_bill_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_history_data = json.dumps({
            "unit_id": 1,
            "amount": 1500.75,
            "date_sent": "2024-08-14",
            "rent_cost": 500,
            "water_cost": 100,
            "cost_per_unit": 5
        })
        add_history = self.client().post('/bill/history/add', data=new_history_data, content_type="application/json", headers=headers)
        self.assertEqual(add_history.status_code, 200)
        response = add_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill history records processed successfully!')

   
    def test_user_logged_in_user_can_get_all_bill_histories(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_histories = self.client().get('/bill/history/list?page=1', content_type="application/json", headers=headers)
        self.assertEqual(fetch_histories.status_code, 200)
        response = fetch_histories.get_json()  # Use get_json() instead of data.decode()
        self.assertIn('BillHistory', response)
        
        # Add more specific assertions
        self.assertIsInstance(response['BillHistory'], list)
        self.assertTrue(len(response['BillHistory']) > 0)
        
        # Check the structure of the first item
        first_item = response['BillHistory'][0]
        expected_keys = ['id', 'unit_id', 'amount', 'date_sent', 'res_room', 'residentName', 'residentEmail', 'currentNumberOfUnits', 'previousNumberOfUnits']
        for key in expected_keys:
            self.assertIn(key, first_item)

    def test_user_logged_in_user_can_update_bill_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_history_data = json.dumps({
            "amount": 1800.50,
            "date_sent": "2024-08-15",
            "rent_cost": 550,
            "water_cost": 120,
            "cost_per_unit": 6
        })
        update_history = self.client().put('/bill/history/edit/1', data=update_history_data, content_type="application/json", headers=headers)
        self.assertEqual(update_history.status_code, 200)
        response = update_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill history record updated successfully!')

    def test_user_logged_in_user_cannot_update_nonexistent_bill_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        update_history_data = json.dumps({
            "amount": 1800.50,
            "date_sent": "2024-08-15",
            "rent_cost": 550,
            "water_cost": 120,
            "cost_per_unit": 6
        })
        update_history = self.client().put('/bill/history/edit/100', data=update_history_data, content_type="application/json", headers=headers)
        self.assertEqual(update_history.status_code, 404)
        response = update_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill history record not found')

    def test_user_logged_in_user_can_delete_bill_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        delete_history = self.client().delete('/bill/history/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_history.status_code, 200)
        response = delete_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill history record deleted successfully!')

    def test_user_logged_in_user_cannot_delete_nonexistent_bill_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        delete_history = self.client().delete('/bill/history/del/100', content_type="application/json", headers=headers)
        self.assertEqual(delete_history.status_code, 404)
        response = delete_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Bill history record not found')

    def test_user_without_valid_token_cannot_add_bill_history(self):
        headers = headerSetUp(self, 0, self.user_details)
        new_history_data = json.dumps({
            "bill_id": 1,
            "amount": 1500.75,
            "date_sent": "2024-08-14",
            "rent_cost": 500,
            "water_cost": 100,
            "cost_per_unit": 5
        })
        add_history = self.client().post('/bill/history/add', data=new_history_data, content_type="application/json", headers=headers)
        self.assertEqual(add_history.status_code, 401)
        response = add_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_get_bill_histories(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_histories = self.client().get('/bill/history/list', content_type="application/json", headers=headers)
        self.assertEqual(fetch_histories.status_code, 401)
        response = fetch_histories.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_update_bill_history(self):
        headers = headerSetUp(self, 0, self.user_details)
        update_history_data = json.dumps({
            "amount": 1800.50,
            "date_sent": "2024-08-15",
            "rent_cost": 500,
            "water_cost": 100,
            "cost_per_unit": 6
        })
        update_history = self.client().put('/bill/history/edit/1', data=update_history_data, content_type="application/json", headers=headers)
        self.assertEqual(update_history.status_code, 401)
        response = update_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_without_valid_token_cannot_delete_bill_history(self):
        headers = headerSetUp(self, 0, self.user_details)
        delete_history = self.client().delete('/bill/history/del/1', content_type="application/json", headers=headers)
        self.assertEqual(delete_history.status_code, 401)
        response = delete_history.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

if __name__ == '__main__':
    unittest.main()
