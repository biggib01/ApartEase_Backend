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

class TestResidentCRUD(unittest.TestCase):
    """Testcase for blueprint for residents CRUD"""

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

            res1 = Resident(name='supachok jrirarojkul', lineId='line1', roomNumber='101')
            res2 = Resident(name='puwadee pleumpiti', lineId='line2', roomNumber='102')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(res1)
            db.session.add(res2)
            db.session.commit()

    def tearDown(self):
        # Pop the application context
        self.app_context.pop()


    def test_user_logged_in_user_can_add_resident(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_resident_data = json.dumps({
            'name': 'John Doe',
            'lineId': 'line1',
            'roomNumber': '201'
        })
        add_resident = self.client().post('/resident/add', data=new_resident_data, content_type="application/json",
                                          headers=headers)
        self.assertEqual(add_resident.status_code, 201)
        response = add_resident.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], 'new residents data created')

    def test_user_logged_in_user_cannot_add_a_resident_in_the_duplicate_room_number(self):
        headers = headerSetUp(self, 1, self.user_details)
        new_resident_data = json.dumps({
            'name': 'Chart Chaiyapoom',
            'lineId': 'lineNum',
            'roomNumber': '101'
        })
        add_resident = self.client().post('/resident/add', data=new_resident_data, content_type="application/json",
                                          headers=headers)
        self.assertEqual(add_resident.status_code, 409)
        response = add_resident.data.decode()
        self.assertEqual(ast.literal_eval(response)['message'], "There's other resident in this room already!")

    def test_user_without_valid_token_cannot_add_resident(self):
        headers = headerSetUp(self, 0, self.user_details)
        new_resident_data = json.dumps({
            'name': 'John Seed',
            'lineId': 'line1',
            'roomNumber': '101'
        })
        add_resident = self.client().post('/resident/add', data=new_resident_data, content_type="application/json",
                                          headers=headers)
        response = add_resident.data.decode()
        self.assertEqual(add_resident.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_get_residents_list_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list?page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Resident':
                                                          [{
                                                              'id': 1,
                                                              'lineId': 'line1',
                                                              'name': 'supachok jrirarojkul',
                                                              'roomNumber': '101'
                                                          },{
                                                              'id': 2,
                                                              'lineId': 'line2',
                                                              'name': 'puwadee pleumpiti',
                                                              'roomNumber': '102'
                                                          },
                                                              {
                                                                  'page': 1,
                                                                  'total_pages': 1,
                                                                  'total_resident': 2
                                                              }
                                                          ]})

    def test_user_logged_in_user_cannot_get_residents_list_before_having_data_in_DB(self):
        db.session.execute(delete(Resident))
        db.session.commit()

        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list?page=1', data=self.user_details,
                                            content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "There is no residents data yet!"})

    def test_user_logged_in_user_cannot_get_residents_list_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list?page=100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'There is no residents data left!'})

    def test_user_without_valid_token_cannot_get_residents_list(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_residents = self.client().get('/resident/list', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_get_residents_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Resident':
                                                          {'id': 1,
                                                           'lineId': 'line1',
                                                           'name': 'supachok jrirarojkul',
                                                           'roomNumber': '101'}})

    def test_user_logged_in_user_cannot_get_residents_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "The resident does not exist"})

    def test_user_without_valid_token_cannot_get_residents_by_id(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_residents = self.client().get('/resident/list/1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_search_residents_by_room_number(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/room?query=101&page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Resident':
                                                          [
                                                              {
                                                                  'id': 1,
                                                                  'lineId': 'line1',
                                                                  'name': 'supachok jrirarojkul',
                                                                  'roomNumber': '101'
                                                              },
                                                              {
                                                                  'page': 1,
                                                                  'total_pages': 1
                                                              }
                                                          ]
        })

    def test_user_logged_in_user_cannot_search_residents_by_non_exist_room_number_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/room?query=901&page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'The resident with the room number does not exist'})

    def test_user_logged_in_user_cannot_search_residents_by_room_number_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/room?query=101&page=100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'There is no residents data left!'})

    def test_user_without_valid_token_cannot_search_residents_by_room_number(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_residents = self.client().get('/resident/list/room?query=101&page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_search_residents_by_name_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/name?query=supachok&page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 200)
        self.assertEqual(ast.literal_eval(response), {'Resident':
                                                          [
                                                              {
                                                                  'id': 1,
                                                                  'lineId': 'line1',
                                                                  'name': 'supachok jrirarojkul',
                                                                  'roomNumber': '101'
                                                              },
                                                              {
                                                                  'page': 1,
                                                                  'total_pages': 1
                                                              }
                                                          ]
        })

    def test_user_logged_in_user_cannot_search_residents_by_name_with_page_more_than_total_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/name?query=supachok&page=100', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'There is no residents data left!'})

    def test_user_logged_in_user_cannot_search_residents_by_non_exist_name_with_page(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/name?query=lokmnji&page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "The resident with the name does not exist"})

    def test_user_logged_in_user_get_a_blank_list_by_search_residents_without_input_name(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().get('/resident/list/name?page=1', data=self.user_details, content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 200)
        self.assertEqual(ast.literal_eval(response), [])

    def test_user_without_valid_token_cannot_search_residents_by_name_with_page(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_residents = self.client().get('/resident/list/name?query=supachok&page=1', data=self.user_details,
                                            content_type="application/json",
                                            headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_update_all_residents_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': 'Supachai Pleumpiti',
            'lineId': '1line',
            'roomNumber': '103'
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'message': 'Resident data has been update'})

    def test_user_logged_in_user_can_update_only_residents_name_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': 'Supachai Pleumpiti',
            'lineId': '',
            'roomNumber': ''
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'message': 'Resident data has been update'})

    def test_user_logged_in_user_can_update_only_residents_lineId_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': '',
            'lineId': '1line',
            'roomNumber': ''
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'message': 'Resident data has been update'})

    def test_user_logged_in_user_can_update_only_residents_roomNumber_field_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': '',
            'lineId': '',
            'roomNumber': '103'
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 201)
        self.assertEqual(ast.literal_eval(response), {'message': 'Resident data has been update'})

    def test_user_logged_in_user_cannot_update_residents_by_id_with_the_same_room_number_of_others(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': 'Supachai Pleumpiti',
            'lineId': '1line',
            'roomNumber': '102'
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 409)
        self.assertEqual(ast.literal_eval(response), {"message": "There's other resident in this room already!"})

    def test_user_logged_in_user_cannot_update_residents_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        edit_resident_data = json.dumps({
            'name': 'Supachai Pleumpiti',
            'lineId': '1line',
            'roomNumber': '103'
        })
        fetch_residents = self.client().put('/resident/edit/100', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {"message": "There's no resident exists!"})


    def test_user_without_valid_token_cannot_update_residents_by_id(self):
        headers = headerSetUp(self, 0, self.user_details)
        edit_resident_data = json.dumps({
            'name': 'Supachai Pleumpiti',
            'lineId': '1line',
            'roomNumber': '102'
        })
        fetch_residents = self.client().put('/resident/edit/1', data=edit_resident_data,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')

    def test_user_logged_in_user_can_delete_residents_by_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().delete('/resident/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 202)
        self.assertEqual(ast.literal_eval(response), {'message': 'resident deleted'})

    def test_user_logged_in_user_cannot_delete_residents_by_non_exist_id(self):
        headers = headerSetUp(self, 1, self.user_details)
        fetch_residents = self.client().delete('/resident/del/100', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 404)
        self.assertEqual(ast.literal_eval(response), {'message': 'The resident does not exist'})

    def test_user_without_valid_token_cannot_delete_residents_by_id(self):
        headers = headerSetUp(self, 0, self.user_details)
        fetch_residents = self.client().delete('/resident/del/1', data=self.user_details,
                                             content_type="application/json",
                                             headers=headers)
        response = fetch_residents.data.decode()
        self.assertEqual(fetch_residents.status_code, 401)
        self.assertEqual(ast.literal_eval(response)['message'], 'Invalid token!')