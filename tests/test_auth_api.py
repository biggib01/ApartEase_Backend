"""Tests for User Authentication"""
import unittest
import json
import ast

from werkzeug.security import generate_password_hash

from library.main import app, db
from config import app_config
from library.model.models import Users, Roles

class TestAuth(unittest.TestCase):
    """Testcase for blueprint for authentication"""

    def setUp(self):
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client
        self.user_details = json.dumps({
            'password': 'user',
            'username': 'user'
        })
        self.admin_details = json.dumps({
            'password': 'admin',
            'username': 'admin'
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
            db.session.commit()

    def test_user_login_as_user(self):
        fetch_user = self.client().post('/login', data=self.user_details, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'User':
                                                          {'role':
                                                               [{
                                                                   'name': 'user'}],
                                                              'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InVzZXIifQ.8BubTzur1pNB3-s0DsBKBYP0c7iWTnhSSbtbQgxjeqU',
                                                              'username': 'user'}})

    def test_user_login_as_admin(self):
        fetch_user = self.client().post('/login', data=self.admin_details, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'User':
                                                          {'role':
                                                               [{
                                                                   'name': 'admin'}],
                                                              'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.1Al8RHoDdEiGxSQ8jYfIdh3l6PFXTsWvaEL_4SHw-yg',
                                                              'username': 'admin'}})

    def test_user_not_input_username(self):
        user_data = json.dumps({
            "username": "",
            "password": "user"
        })
        fetch_user = self.client().post('/login', data=user_data, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(response, 'Could not verify!')

    def test_user_not_input_password(self):
        user_data = json.dumps({
            "username": "user",
            "password": ""
        })
        fetch_user = self.client().post('/login', data=user_data, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(response, 'Could not verify!')


    def test_user_input_wrong_username(self):
        user_data = json.dumps({
            "username": "wrongUsername",
            "password": "user"
        })
        fetch_user = self.client().post('/login', data=user_data, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(response, 'Could not verify user!')


    def test_user_input_wrong_password(self):
        user_data = json.dumps({
            "username": "user",
            "password": "wrongPassword"
        })
        fetch_user = self.client().post('/login', data=user_data, content_type="application/json")
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 403)
        self.assertEqual(response, 'Could not verify password!')
