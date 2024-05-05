import json

from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
import datetime as date
# from datetime import datetime, timedelta
from library.main import db, app
from library.models import User, token_required, Resident, Unit


# register route
@app.route('/signup', methods=['POST'])
def signup_user(): 
    data = request.get_json() 
    hashed_password = generate_password_hash(data['password'], method='sha256')
    role = data['admin']
    
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        new_user = User(public_id=str(uuid.uuid4()), username=data['username'], password=hashed_password, admin=role)
        db.session.add(new_user) 
        db.session.commit() 

        return jsonify({'message': 'registered successfully'}), 201
    else:
        return make_response(jsonify({"message": "User already exists!"}), 409)

# user login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = User.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'public_id': user.public_id}, app.config['SECRET_KEY'], 'HS256')
        return make_response(jsonify({'token': token}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


# edit user's info
@app.route('/user/edit/<string:uid>', methods=['POST'])
@token_required
def edit_user(current_user, uid):

    change_data = request.get_json()
    change_username = change_data['username']
    change_password = generate_password_hash(change_data['password'], method='sha256')
    change_role = change_data['admin']

    user = User.query.filter_by(id=uid).first()

    if user:
        user.username = change_username
        user.password = change_password
        user.admin = change_role

        db.session.commit()

        return jsonify({'message': 'User data has been update'}), 201
    else:
        return make_response(jsonify({"message": "There's no user exists!"}), 409)


# get all users
@app.route('/user/list', methods=['GET'])
@token_required
def get_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['has_admin_role'] = user.admin
        output.append(user_data)

    return jsonify({'Books': output})

# get user by id
@app.route('/user/list/<uid>', methods=['GET'])
@token_required
def get_user(current_user, uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'message': 'book does not exist'})

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['has_admin_role'] = user.admin

    return jsonify({'message': user_data})


# deleting a user
@app.route('/user/del/<uid>', methods=['DELETE'])
@token_required
def delete_book(current_user, uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'message': 'User does not exist'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


#  add a resident
@app.route('/resident/add', methods=['POST'])
@token_required
def create_resident(current_user):
    '''adds a new book to collection!'''
    data = request.get_json()
    room_check = Resident.query.filter_by(roomNumber=data['roomNumber']).first()
    if room_check:
        return make_response(jsonify({"message": "There's other resident in this room already!"}), 409)
    else:
        resident = Resident.query.filter_by(name=data['name']).first()
        if resident:
            return make_response(jsonify({"message": "Resident with same name already exists!"}), 409)
        else:
            new_resident = Resident(name=data['name'], lineId=data['lineId'], roomNumber=data['roomNumber'])
            db.session.add(new_resident)
            db.session.commit()

            return jsonify({'message': 'new residents data created'})

#  add a electric unit data
@app.route('/unit/add', methods=['POST'])
@token_required
def create_unit(current_user):
    '''adds a new book to collection!'''
    data = request.get_json()

    new_unit = Unit(numberOfUnits=data['numberOfUnits'],
                    date=date.datetime.now(),
                    extractionStatus=data['extractionStatus'],
                    res_room=data['roomNumber'])
    db.session.add(new_unit)
    db.session.commit()
    return jsonify({'message' : 'new unit data created'})

# get all residents
@app.route('/resident/list', methods=['GET'])
@token_required
def get_residents(current_user):
    residents = Resident.query.all()
    output = []
    for resident in residents:
        resident_data = {}
        resident_data['id'] = resident.id
        resident_data['name'] = resident.name
        resident_data['lineId'] = resident.lineId
        resident_data['roomNumber'] = resident.roomNumber

        unit_output = []
        for unit in resident.unit:
            unit_data = {}
            unit_data['id'] = unit.id
            unit_data['numberOfUnits'] = unit.numberOfUnits
            unit_data['extractionStatus'] = unit.extractionStatus

            unit_output.append(unit_data)

        resident_data['unitList'] = unit_output
        output.append(resident_data)

    return jsonify({'Resident': output})