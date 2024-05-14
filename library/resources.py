import json
from operator import and_

from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
import datetime as date
from library.main import db, app, BaseQuery
from library.models import User, token_required, Resident, Unit
import difflib


# register route [http://localhost/signup]
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

# user login route [http://localhost/login]
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


# edit user's info [http://localhost/user/edit/x]
@app.route('/user/edit/<uid>', methods=['POST'])
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


# get all users [http://localhost/user/list]
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

    return jsonify({'Users': output})

# get user by id [http://localhost/user/list/x]
@app.route('/user/list/<uid>', methods=['GET'])
@token_required
def get_user(current_user, uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'message': 'user does not exist'})

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['has_admin_role'] = user.admin

    return jsonify({'message': user_data})


# deleting a user [http://localhost/user/del/x]
@app.route('/user/del/<uid>', methods=['DELETE'])
@token_required
def delete_user(current_user, uid):
    user = User.query.filter_by(id=uid).first()
    if not user:
        return jsonify({'message': 'User does not exist'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

#--------------------------------------------------#

#  add a resident [http://localhost/resident/add]
@app.route('/resident/add', methods=['POST'])
@token_required
def create_resident(current_user):
    data = request.get_json()
    room_check = Resident.query.filter_by(roomNumber=data['roomNumber']).first()
    if room_check:
        return make_response(jsonify({"message": "There's other resident in this room already!"}), 409)
    else:
        new_resident = Resident(name=data['name'].lower(), lineId=data['lineId'], roomNumber=data['roomNumber'])
        db.session.add(new_resident)
        db.session.commit()

        return jsonify({'message': 'new residents data created'})

# get all residents with pagination [http://localhost/resident/list?page=x]
@app.route('/resident/list', methods=['GET'])
@token_required
def get_residents(current_user):
    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    residents = Resident.query.all()

    total_pages = (len(residents) + per_page - 1) // per_page
    item_on_page = residents[start:end]

    output = []
    for resident in item_on_page:
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

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Resident': output})

# get a resident by id [http://localhost/resident/list/x]
@app.route('/resident/list/<res_id>', methods=['GET'])
@token_required
def get_resident(current_user, res_id):
    resident = Resident.query.filter_by(id=res_id).first()

    if not resident:
        return jsonify({'message': 'The resident does not exist'})

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


    return jsonify({'Resident': resident_data})

# get resident by room number for search [http://localhost/resident/list/room?query=x]
@app.route('/resident/list/room', methods=['GET'])
@token_required
def get_resident_by_roomNumber(current_user):
    query = request.args.get('query', type=str)

    resident = Resident.query.filter_by(roomNumber=query).all()

    output = []

    if not resident:
        return jsonify({'message': 'The resident with the room number does not exist'})

    else:
        for resident in resident:
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

# get resident by name for search [http://localhost/resident/list/name?query=x]
@app.route('/resident/list/name', methods=['GET'])
@token_required
def get_resident_by_name(current_user):
    query = request.args.get('query', type=str)

    list_name = []

    data_name = Resident.query.all()

    for names in data_name:
        list_name.append(names.name)

    result_name = difflib.get_close_matches(query, list_name, cutoff=0.6)

    resident = Resident.query.filter(Resident.name.in_(result_name))

    output = []

    for resident in resident:
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

    if len(output) is 0:
        return jsonify({'message': 'The resident with the name does not exist'})
    else:
        return jsonify({'Resident': output})

# deleting a resident [http://localhost/resident/del/x]
@app.route('/resident/del/<res_id>', methods=['DELETE'])
@token_required
def delete_resident(current_user, res_id):
    resident = Resident.query.filter_by(id=res_id).first()
    if not resident:
        return jsonify({'message': 'The resident does not exist'})

    db.session.delete(resident)
    db.session.commit()
    return jsonify({'message': 'resident deleted'})

# update resident by id [http://localhost/resident/edit/x]
@app.route('/resident/edit/<res_id>', methods=['POST'])
@token_required
def update_resident(current_user, res_id):

    change_data = request.get_json()
    change_name = change_data['name'].lower()
    change_lineId = change_data['lineId']
    change_roomNumber = change_data['roomNumber']

    resident = Resident.query.filter_by(id=res_id).first()

    if resident:
        check_room = Resident.query.filter_by(roomNumber=change_roomNumber).first()

        if check_room and check_room.roomNumber != resident.roomNumber:
            return make_response(jsonify({"message": "There's other resident in this room already!"}), 409)
        else:
            resident.name = change_name
            resident.lineId = change_lineId
            resident.roomNumber = change_roomNumber

            db.session.commit()

            return jsonify({'message': 'Resident data has been update'}), 201
    else:
        return make_response(jsonify({"message": "There's no resident exists!"}), 409)

#--------------------------------------------------#

#  add a unit, [http://localhost/unit/add]
@app.route('/unit/add', methods=['POST'])
@token_required
def create_unit(current_user):
    data = request.get_json()

    new_unitRecord = Unit(numberOfUnits=data['numberOfUnits'],
                     date=date.datetime.now(),
                     extractionStatus=data['extractionStatus'],
                     approveStatus=False,
                     res_room=data['res_room'])
    db.session.add(new_unitRecord)
    db.session.commit()

    return jsonify({'message' : 'new record created'})

# get record list by id [http://localhost/unit/list/x]
@app.route('/unit/list/<unit_id>', methods=['GET'])
@token_required
def get_unit(current_user, unit_id):
    unit_record = Unit.query.filter_by(id=unit_id).first()

    if not unit_record:
        return jsonify({'message': 'The record does not exist'})

    record_data = {}
    record_data['id'] = unit_record.id
    record_data['numberOfUnits'] = unit_record.numberOfUnits
    record_data['date'] = unit_record.date
    record_data['extractionStatus'] = unit_record.extractionStatus
    record_data['approveStatus'] = unit_record.approveStatus
    record_data['res_room'] = unit_record.res_room

    return jsonify({'Unit': record_data})

def toDate(dateString):
    return date.datetime.strptime(dateString, "%Y-%m-%d").date()

# get record list by date(month) [http://localhost/unit/list/date?page=x&start=%Y-%m-%d&end=%Y-%m-%d]
@app.route('/unit/list/date', methods=['GET'])
@token_required
def get_unit_by_date(current_user):
    startDate = request.args.get('start', type=toDate)
    endDate = request.args.get('end', type=toDate)
    # pagination
    page = request.args.get('page', type=int)

    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.filter(and_(Unit.date <= endDate, Unit.date >= startDate)).all()

    total_pages = (len(unit_record) + per_page - 1) // per_page
    item_on_page = unit_record[start:end]

    output = []
    for record in item_on_page:
        record_data = {}
        record_data['id'] = record.id
        record_data['numberOfUnits'] = record.numberOfUnits
        record_data['date'] = record.date
        record_data['extractionStatus'] = record.extractionStatus
        record_data['approveStatus'] = record.approveStatus
        record_data['res_room'] = record.res_room
        output.append(record_data)

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Unit': output})

# get record list by room number [http://localhost/unit/list/room?page=x&query=x]
@app.route('/unit/list/room', methods=['GET'])
@token_required
def get_unit_by_room(current_user):
    query = request.args.get('query', type=str)
    # pagination
    page = request.args.get('page', type=int)

    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.filter(Unit.res_room.like(query)).all()

    total_pages = (len(unit_record) + per_page - 1) // per_page
    item_on_page = unit_record[start:end]

    output = []
    for record in item_on_page:
        record_data = {}
        record_data['id'] = record.id
        record_data['numberOfUnits'] = record.numberOfUnits
        record_data['date'] = record.date
        record_data['extractionStatus'] = record.extractionStatus
        record_data['approveStatus'] = record.approveStatus
        record_data['res_room'] = record.res_room
        output.append(record_data)

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Unit': output})

# get all records with pagination [http://localhost/unit/list]
@app.route('/unit/list', methods=['GET'])
@token_required
def get_units(current_user):
    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.all()

    total_pages = (len(unit_record) + per_page - 1) // per_page
    item_on_page = unit_record[start:end]

    output = []
    for record in item_on_page:
        record_data = {}
        record_data['id'] = record.id
        record_data['numberOfUnits'] = record.numberOfUnits
        record_data['date'] = record.date
        record_data['extractionStatus'] = record.extractionStatus
        record_data['approveStatus'] = record.approveStatus
        record_data['res_room'] = record.res_room
        output.append(record_data)

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Unit': output})

# deleting a record [http://localhost/unit/del/x]
@app.route('/unit/del/<rec_id>', methods=['DELETE'])
@token_required
def delete_unit(current_user, rec_id):
    unit_record = Unit.query.filter_by(id=rec_id).first()
    if not unit_record:
        return jsonify({'message': 'record does not exist'})

    db.session.delete(unit_record)
    db.session.commit()
    return jsonify({'message': 'Record deleted'})

# update record [http://localhost/unit/edit/x]
@app.route('/unit/edit/<rec_id>', methods=['POST'])
@token_required
def update_unit(current_user, rec_id):

    date_format = '%Y-%m-%d'

    change_data = request.get_json()
    change_numberOfUnits = change_data['numberOfUnits']
    change_date = date.datetime.strptime(change_data['date'], date_format)
    change_extractionStatus = change_data['extractionStatus']
    change_approveStatus = change_data['approveStatus']
    change_room = change_data['res_room']

    unit_record = Unit.query.filter_by(id=rec_id).first()

    if unit_record:
        unit_record.numberOfUnits = change_numberOfUnits
        unit_record.date = change_date
        unit_record.extractionStatus = change_extractionStatus
        unit_record.approveStatus = change_approveStatus
        unit_record.res_room = change_room

        db.session.commit()

        return jsonify({'message': 'Record data has been update'}), 201
    else:
        return make_response(jsonify({"message": "There's no record exists!"}), 409)
