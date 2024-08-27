import unittest
import json
import ast
from sqlalchemy import delete
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident, BillHistory
from tests.function_for_test.test_function import headerSetUp

class TestBillHistoryRoutes(unittest.TestCase):
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

    # def test_add_unit_history(self):
    #     headers = headerSetUp(self, 1, self.user_details)
    #     with open('tests/test_data/unit_history_data.json') as f:
    #         data = json.load(f)
    #     response = self.client().post('/unit/history/add', data=json.dumps(data), content_type='application/json', headers=headers)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('Unit history record added successfully!', response.get_data(as_text=True))

    def test_get_unit_history(self):
        headers = headerSetUp(self, 1, self.user_details)
        response = self.client().get('/unit/history/list', content_type='application/json', headers=headers)
        self.assertEqual(response.status_code, 200)

    # def test_update_unit_history(self):
    #     headers = headerSetUp(self, 1, self.user_details)
    #     with open('tests/test_data/unit_history_data.json') as f:
    #         data = json.load(f)
    #     self.client().post('/unit/history/add', data=json.dumps(data), content_type='application/json', headers=headers)
    #     update_data = {
    #         "numberOfUnits": "2002"
    #     }
    #     response = self.client().put('/unit/history/edit/1', data=json.dumps(update_data), content_type='application/json', headers=headers)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('Unit history record updated successfully!', response.get_data(as_text=True))

    # def test_delete_unit_history(self):
    #     headers = headerSetUp(self, 1, self.user_details)
    #     with open('tests/test_data/unit_history_data.json') as f:
    #         data = json.load(f)
    #     self.client().post('/unit/history/add', data=json.dumps(data), content_type='application/json', headers=headers)
    #     response = self.client().delete('/unit/history/del/1', content_type='application/json', headers=headers)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('Unit history record deleted successfully!', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
