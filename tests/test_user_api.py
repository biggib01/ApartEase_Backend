"""Tests for Resident CRUD"""
import unittest
import json
import ast

from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident
from tests.function_for_test.test_function import headerSetUp


class TestUserCRUD(unittest.TestCase):
    """Testcase for blueprint for residents CRUD"""

    def setUp(self):
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client
        self.admin_details = json.dumps({
            'password': 'admin',
            'username': 'admin'
        })
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

            res1 = Resident(name='supachok jrirarojkul', lineId='line1', roomNumber='101')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(res1)
            db.session.commit()

    def tearDown(self):
        # Pop the application context
        self.app_context.pop()

    def test_user_role_admin_logged_in_user_can_add_user(self):
        headers = headerSetUp(self, 1, self.admin_details)
        new_user_data = json.dumps({
            'username': 'test1',
            'password': 'test1',
            'role': 'user'
        })
        add_user = self.client().post('/user/add', data=new_user_data, content_type="application/json",
                                          headers=headers)
        response = add_user.data.decode()
        self.assertEqual(add_user.status_code, 201)
        self.assertEqual(ast.literal_eval(response)['message'], 'User created')

    def test_user_role_admin_logged_in_user_cannot_add_user_with_non_exist_role(self):
        headers = headerSetUp(self, 1, self.admin_details)
        new_user_data = json.dumps({
            'username': 'test2',
            'password': 'test2',
            'role': 'noRole'
        })
        add_user = self.client().post('/user/add', data=new_user_data, content_type="application/json",
                                          headers=headers)
        response = add_user.data.decode()
        self.assertEqual(add_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response)['message'], 'The role dose not exists')

    def test_user_role_admin_logged_in_user_cannot_add_user_with_the_same_username(self):
        headers = headerSetUp(self, 1, self.admin_details)
        new_user_data = json.dumps({
            'username': 'user',
            'password': 'test1',
            'role': 'user'
        })
        add_user = self.client().post('/user/add', data=new_user_data, content_type="application/json",
                                      headers=headers)
        response = add_user.data.decode()
        self.assertEqual(add_user.status_code, 409)
        self.assertEqual(ast.literal_eval(response)['message'], 'User already exists!')

    def test_user_not_role_admin_logged_in_user_cannot_add_user(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_user_data = json.dumps({
            'username': 'test1',
            'password': 'test1',
            'role': 'user'
        })
        add_user = self.client().post('/user/add', data=new_user_data, content_type="application/json",
                                          headers=headers)
        response = add_user.data.decode()
        self.assertEqual(add_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')

    def test_user_without_valid_token_cannot_add_user(self):
        headers = headerSetUp(self, 0, self.admin_details)
        new_user_data = json.dumps({
            'username': 'test2',
            'password': 'test2',
            'role': 'user'
        })
        add_user = self.client().post('/user/add', data=new_user_data, content_type="application/json",
                                          headers=headers)
        response = add_user.data.decode()
        self.assertEqual(add_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_get_user_list_with_page(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().get('/user/list?page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'User': [
            {'id': 1, 'role': 'user', 'username': 'user'},
            {'id': 2, 'role': 'admin', 'username': 'admin'},
            {'page': 1, 'total_pages': 1, 'total_users': 2}]})

    def test_user_role_admin_logged_in_user_cannot_get_user_list_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().get('/user/list?page=100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'There is no user data left!'})

    def test_user_not_role_admin_logged_in_user_cannot_get_user_list(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_user = self.client().get('/user/list', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')


    def test_user_without_valid_token_cannot_get_user_list(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_user = self.client().get('/user/list', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_get_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().get('/user/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'User': {'id': 1, 'role': 'user', 'username': 'user'}})

    def test_user_role_admin_logged_in_user_cannot_get_user_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().get('/user/list/100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'user does not exist'})

    def test_user_not_role_admin_logged_in_user_cannot_get_user_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_user = self.client().get('/user/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')

    def test_user_without_valid_token_cannot_get_user_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_user = self.client().get('/user/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_update_all_field_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "test2",
            "role": "admin"
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'User data has been update'})

    def test_user_role_admin_logged_in_user_can_update_only_username_field_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "",
            "role": ""
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'User data has been update'})

    def test_user_role_admin_logged_in_user_can_update_only_password_field_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "",
            "password": "test2",
            "role": ""
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'User data has been update'})

    def test_user_role_admin_logged_in_user_can_update_only_role_field_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "",
            "password": "",
            "role": "admin"
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'User data has been update'})

    def test_user_role_admin_logged_in_user_cannot_update_user_by_id_with_non_exist_role(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "test2",
            "role": "noRole"
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "The role dose not exists"})

    def test_user_role_admin_logged_in_user_cannot_update_user_by_non_exist_user_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "test2",
            "role": "admin"
        })
        fetch_user = self.client().put('/user/edit/100', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "There's no user exists!"})

    def test_user_not_role_admin_logged_in_user_cannot_update_user_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "test2",
            "role": "admin"
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response), {'message': 'access denied'})

    def test_user_without_valid_token_cannot_update_user_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        edit_user_data = json.dumps({
            "username": "test2",
            "password": "test2",
            "role": "admin"
        })
        fetch_user = self.client().put('/user/edit/1', data=edit_user_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_delete_user_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().delete('/user/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'User deleted'})

    def test_user_role_admin_logged_in_user_cannot_delete_user_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_user = self.client().delete('/user/del/100', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'User does not exist'})

    def test_user_not_role_admin_logged_in_user_cannot_delete_user_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_user = self.client().delete('/user/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response), {'message': 'access denied'})

    def test_user_without_valid_token_cannot_delete_user_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_user = self.client().delete('/user/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_user.data.decode()
        self.assertEqual(fetch_user.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')
