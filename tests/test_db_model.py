"""Tests for repr of Model"""
import unittest
import json
import datetime as date
from werkzeug.security import generate_password_hash
from library.main import app, db
from config import app_config
from library.model.models import Users, Roles, Resident, Unit
from tests.function_for_test.test_function import headerSetUp

class TestModelRepr(unittest.TestCase):
    """Testcase for blueprint for repr of Model"""

    def setUp(self):
        self.app = app
        self.app.config.from_object(app_config['testing'])
        self.client = self.app.test_client
        self.user_details = json.dumps({
            'password': 'user',
            'username': 'user'
        })
        self.resident_details = json.dumps({
            'name': 'supachok jrirarojkul',
            'lineId': 'line1',
            'roomNumber': '101'
        })
        self.unit_details = json.dumps({
            "approveStatus": False,
            "date": "Thu, 13 Jun 2024 00:00:00 GMT",
            "extractionStatus": "Extract successfully",
            "id": 1,
            "numberOfUnits": "1001",
            "res_room": "101"
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
            res2 = Resident(name='puwadee pleumpiti', lineId='line2', roomNumber='102')

            user.roles.append(role_user)
            admin.roles.append(role_admin)

            db.session.add(user)
            db.session.add(admin)
            db.session.add(res1)
            db.session.add(res2)
            db.session.commit()

    def test_user_repr(self):
        """Test the __repr__ method of the Users model."""
        # Load user data from JSON
        user_data = json.loads(self.user_details)

        # Create a Users instance using the loaded data
        user = Users(username=user_data['username'], password=user_data['password'])
        expected_repr = '<User {}>'.format(user_data['username'])

        # Check if the __repr__ method returns the expected string
        self.assertEqual(repr(user), expected_repr)

    def test_resident_repr(self):
        """Test the __repr__ method of the Users model."""
        # Load user data from JSON
        resident_data = json.loads(self.resident_details)

        # Create a Users instance using the loaded data
        resident = Resident(name=resident_data['name'], lineId=resident_data['lineId'], roomNumber=resident_data['roomNumber'])
        expected_repr = '<Resident "{}">'.format(resident_data['name'])

        # Check if the __repr__ method returns the expected string
        self.assertEqual(repr(resident), expected_repr)

    def test_unit_repr(self):
        """Test the __repr__ method of the Users model."""
        # Load user data from JSON
        unit_data = json.loads(self.unit_details)

        # Create a Users instance using the loaded data
        unit_record = Unit(numberOfUnits=unit_data['numberOfUnits'],
                        id= unit_data['id'],
                        date=date.datetime.now(),
                        extractionStatus=unit_data['extractionStatus'],
                        approveStatus=False,
                        res_room=unit_data['res_room'])
        expected_repr = '<Unit "{}">'.format(unit_data['id'])

        # Check if the __repr__ method returns the expected string
        self.assertEqual(repr(unit_record), expected_repr)
