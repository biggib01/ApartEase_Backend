"""Tests for Resident CRUD"""
import unittest
import json
import ast
from sqlalchemy import delete
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident
from tests.function_for_test.test_function import headerSetUp


class TestRoleCRUD(unittest.TestCase):
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

            res1 = Resident(name='supachok jrirarojkul', lineId='line1', roomNumber='101')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(res1)
            db.session.commit()

    def test_user_role_admin_logged_in_user_can_add_role(self):
        headers = headerSetUp(self, 1, self.admin_details)
        new_role_data = json.dumps({
            'role_name': 'roleTest'
        })
        add_role = self.client().post('/role/add', data=new_role_data, content_type="application/json",
                                          headers=headers)
        response = add_role.data.decode()
        self.assertEqual(add_role.status_code, 200)
        self.assertEqual(ast.literal_eval(response)['message'], 'new role created')

    def test_user_role_admin_logged_in_user_cannot_add_role_with_the_same_role_name(self):
        headers = headerSetUp(self, 1, self.admin_details)
        new_role_data = json.dumps({
            'role_name': 'admin'
        })
        add_role = self.client().post('/role/add', data=new_role_data, content_type="application/json",
                                          headers=headers)
        response = add_role.data.decode()
        self.assertEqual(add_role.status_code, 409)
        self.assertEqual(ast.literal_eval(response)['message'], 'The role already exist!')

    def test_user_not_role_admin_logged_in_user_cannot_add_role(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_role_data = json.dumps({
            'role_name': 'roleTest'
        })
        add_role = self.client().post('/role/add', data=new_role_data, content_type="application/json",
                                          headers=headers)
        response = add_role.data.decode()
        self.assertEqual(add_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')

    def test_user_without_valid_token_cannot_add_role(self):
        headers = headerSetUp(self, 0, self.admin_details)
        new_role_data = json.dumps({
            'role_name': 'roleTest'
        })
        add_role = self.client().post('/role/add', data=new_role_data, content_type="application/json",
                                          headers=headers)
        response = add_role.data.decode()
        self.assertEqual(add_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_get_role_list_with_page(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().get('/role/list?page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Role':
                                                          [{
                                                              'id': 1,
                                                              'role_name': 'admin'
                                                          }, {
                                                              'id': 2,
                                                              'role_name': 'user'
                                                          },{
                                                              'page': 1,
                                                              'total_pages': 1,
                                                              'total_roles': 2
                                                          }]})

    def test_user_role_admin_logged_in_user_cannot_get_role_list_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().get('/role/list?page=100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'There is no role data left!'})

    def test_user_not_role_admin_logged_in_user_cannot_get_role_list(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_role = self.client().get('/role/list', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')


    def test_user_without_valid_token_cannot_get_role_list(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_role = self.client().get('/role/list', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_get_role_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().get('/role/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Role':
                                                          {
                                                              'id': 1,
                                                              'name': 'admin'
                                                          }})

    def test_user_role_admin_logged_in_user_cannot_get_role_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().get('/role/list/100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 404)
        self.assertEqual(ast.literal_eval(response)['message'], 'Role does not exist')

    def test_user_not_role_admin_logged_in_user_cannot_get_role_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_role = self.client().get('/role/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'access denied')

    def test_user_without_valid_token_cannot_get_role_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_role = self.client().get('/role/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_update_role_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_role_data = json.dumps({
            'role_name': 'roleChange'
        })
        fetch_role = self.client().put('/role/edit/1', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'Role data has been update'})

    def test_user_role_admin_logged_in_user_cannot_update_role_by_id_with_same_role_name(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_role_data = json.dumps({
            'role_name': 'user'
        })
        fetch_role = self.client().put('/role/edit/1', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 409)
        self.assertEqual(ast.literal_eval(response), {'message': 'The role name already exist'})

    def test_user_role_admin_logged_in_user_cannot_update_role_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_role_data = json.dumps({
            'role_name': 'roleChange'
        })
        fetch_role = self.client().put('/role/edit/100', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "The role does not exists!"})

    def test_user_role_admin_logged_in_user_cannot_update_role_by_id_with_no_input(self):
        headers = headerSetUp(self, 1, self.admin_details)
        edit_role_data = json.dumps({
            'role_name': ''
        })
        fetch_role = self.client().put('/role/edit/1', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 400)
        self.assertEqual(ast.literal_eval(response), {"message": "Please input the new name of the role"})

    def test_user_not_role_admin_logged_in_user_cannot_update_role_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_role_data = json.dumps({
            'role_name': 'roleChange'
        })
        fetch_role = self.client().put('/role/edit/1', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response), {'message': 'access denied'})

    def test_user_without_valid_token_cannot_update_role_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        edit_role_data = json.dumps({
            'role_name': 'roleChange'
        })
        fetch_role = self.client().put('/role/edit/1', data=edit_role_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_role_admin_logged_in_user_can_delete_role_by_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().delete('/role/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'message': 'Role deleted'})

    def test_user_role_admin_logged_in_user_cannot_delete_role_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.admin_details)
        fetch_role = self.client().delete('/role/del/100', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'Role does not exist'})

    def test_user_not_role_admin_logged_in_user_cannot_delete_role_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_role = self.client().delete('/role/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response), {'message': 'access denied'})

    def test_user_without_valid_token_cannot_delete_role_by_id(self):
        headers = headerSetUp(self, 0, self.admin_details)
        fetch_role = self.client().delete('/role/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_role.data.decode()
        self.assertEqual(fetch_role.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')
