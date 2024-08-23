import unittest
import json
import ast
from sqlalchemy import delete
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident, Bill
from tests.function_for_test.test_function import headerSetUp
from werkzeug.security import generate_password_hash

class TestBillRoutes(unittest.TestCase):
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

            resident = Resident(name='John Doe', lineId='john.doe@example.com', roomNumber='101')
            db.session.add(resident)

            bill = Bill(amount=1000.0, date='2024-06-13', res_room='101', totalUnit=100, totalBill=500.0)
            db.session.add(bill)

            db.session.commit()

    def test_create_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        with open('tests/test_data/bill_data.json') as f:
            data = json.load(f)
        response = self.client().post('/bill/add', data=json.dumps(data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('New bill created', response.get_data(as_text=True))

    def test_get_bills(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/bill/list', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_update_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        with open('tests/test_data/bill_data.json') as f:
            data = json.load(f)
        self.client().post('/bill/add', data=json.dumps(data), content_type='application/json', headers=headers)
        update_data = {
            "amount": 2000.0
        }
        response = self.client().put('/bill/edit/1', data=json.dumps(update_data), content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bill updated successfully', response.get_data(as_text=True))

    def test_delete_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        with open('tests/test_data/bill_data.json') as f:
            data = json.load(f)
        self.client().post('/bill/add', data=json.dumps(data), content_type='application/json', headers=headers)
        response = self.client().delete('/bill/del/1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bill deleted', response.get_data(as_text=True))

    def test_send_bill_by_email(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().post('/bill/send/1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Bill sent successfully', response.get_data(as_text=True))

    def test_send_bill_by_email_invalid_token(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().post('/bill/send/1', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token!', response.get_data(as_text=True))

    def test_send_bill_by_email_non_existent_bill(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().post('/bill/send/999', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Bill does not exist', response.get_data(as_text=True))

    def test_send_bill_by_email_non_existent_resident(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().post('/bill/send/2', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Resident does not exist', response.get_data(as_text=True))

    def test_send_all_bills_by_email(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().post('/bill/send_all', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('All bills sent successfully', response.get_data(as_text=True))

    def test_send_all_bills_by_email_invalid_token(self):
        headers = headerSetUp(self, 0, self.user_details)
        response = self.client().post('/bill/send_all', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid token!', response.get_data(as_text=True))

    def test_send_all_bills_by_email_no_bills(self):
        headers = headerSetUp(self, 1, self.user_details)
        db.session.execute(delete(Bill))
        db.session.commit()
        response = self.client().post('/bill/send_all', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('No bills found', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
