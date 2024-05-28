import json
from operator import and_

from flask import request, jsonify, make_response
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
import datetime as date
from library.main import db, app, BaseQuery
from library.models import Users, token_required, Resident, Unit, Roles
import difflib
from sqlalchemy.sql import func


# --------------------Authentication------------------------------#

# user login route [http://localhost/login]
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = Users.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'], 'HS256')

        role_output = []

        for role in user.roles:
            role_data = {}
            role_data['name'] = role.name

            role_output.append(role_data)

        user_data = {'username': user.username, 'role': role_output, 'token': token}
        return make_response(jsonify({'User': user_data}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


# --------------------User management------------------------------#

# register route [http://localhost/user/add]
@app.route('/user/add', methods=['POST'])
@token_required
def create_user(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    role_name = data['role']

    user = Users.query.filter_by(username=data['username']).first()

    if not user:
        new_user = Users(username=data['username'],
                         password=hashed_password)

        role = Roles.query.filter_by(name=role_name).first()

        if not role:
            return make_response(jsonify({"message": "The role dose not exists"}), 404)

        new_user.roles.append(role)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User created'}), 201
    else:
        return make_response(jsonify({"message": "User already exists!"}), 409)


# edit user's info [http://localhost/user/edit/x]
@app.route('/user/edit/<uid>', methods=['POST'])
@token_required
def edit_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    change_data = request.get_json()
    change_username = change_data['username']
    change_password = generate_password_hash(change_data['password'], method='sha256')
    change_role = change_data['role']

    user = Users.query.filter_by(id=uid).first()

    if user:
        user.username = change_username
        user.password = change_password

        role = Roles.query.filter_by(name=change_role).first()

        if not role:
            return make_response(jsonify({"message": "The role dose not exists"}), 404)

        user.roles.append(role)

        db.session.commit()

        return make_response(jsonify({'message': 'User data has been update'}), 200)
    else:
        return make_response(jsonify({"message": "There's no user exists!"}), 404)


# get all users [http://localhost/user/list]
@app.route('/user/list', methods=['GET'])
@token_required
def get_users(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    users = Users.query.order_by(Users.id).all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username

        role_list = []

        for role in user.roles:
            role_data = {}
            role_data['name'] = role.name

            role_list.append(role_data)

        user_data['has_admin_role'] = role_list

        output.append(user_data)

    return jsonify({'Users': output})


# get user by id [http://localhost/user/list/x]
@app.route('/user/list/<uid>', methods=['GET'])
@token_required
def get_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    user = Users.query.filter_by(id=uid).first()

    if not user:
        return make_response(jsonify({'message': 'user does not exist'}), 404)

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    role_list = []

    for role in user.roles:
        role_data = {}
        role_data['name'] = role.name

        role_list.append(role_data)

    user_data['has_admin_role'] = role_list

    return jsonify({'message': user_data})


# deleting a user [http://localhost/user/del/x]
@app.route('/user/del/<uid>', methods=['DELETE'])
@token_required
def delete_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    user = Users.query.filter_by(id=uid).first()
    if not user:
        return make_response(jsonify({'message': 'User does not exist'}), 404)

    db.session.delete(user)
    db.session.commit()
    return make_response(jsonify({'message': 'User deleted'}), 200)


# --------------------Role management------------------------------#

#  add a role, [http://localhost/role/add]
@app.route('/role/add', methods=['POST'])
@token_required
def create_role(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    data = request.get_json()

    new_role = Roles(name=data['role_name'])

    role_dup_check = Roles.query.filter_by(name=data['role_name'])

    output = []

    for role in role_dup_check:
        role_data = {}
        role_data['id'] = role.id
        role_data['name'] = role.name

        output.append(role_data)

    if len(output) == 0:

        db.session.add(new_role)
        db.session.commit()

        return make_response(jsonify({'message': 'new role created'}), 200)
    else:
        return make_response(jsonify({'message': 'The role already exist!'}), 409)


# edit role's info [http://localhost/role/edit/x]
@app.route('/role/edit/<rid>', methods=['POST'])
@token_required
def edit_role(current_user, role, rid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    change_data = request.get_json()
    change_role = change_data['role_name']

    role_result = Roles.query.filter_by(id=rid).first()

    if role_result:

        role_result.name = change_role

        db.session.commit()

        return make_response(jsonify({'message': 'Role data has been update'}), 200)
    else:
        return make_response(jsonify({"message": "The role does not exists!"}), 404)


# deleting a role [http://localhost/role/del/x]
@app.route('/role/del/<rid>', methods=['DELETE'])
@token_required
def delete_role(current_user, role, rid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    role = Roles.query.filter_by(id=rid).first()
    if not role:
        return make_response(jsonify({'message': 'Role does not exist'}), 404)

    db.session.delete(role)
    db.session.commit()
    return make_response(jsonify({'message': 'Role deleted'}), 200)


# get all roles [http://localhost/role/list]
@app.route('/role/list', methods=['GET'])
@token_required
def get_roles(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    roles = Roles.query.all()
    output = []
    for role in roles:
        user_data = {}
        user_data['id'] = role.id
        user_data['role_name'] = role.name

        output.append(user_data)

    return jsonify({'Roles': output})


# get role by id [http://localhost/role/list/x]
@app.route('/role/list/<rid>', methods=['GET'])
@token_required
def get_role(current_user, role, rid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    role_result = Roles.query.filter_by(id=rid).first()

    if not role_result:
        return make_response(jsonify({'message': 'Role does not exist'}), 404)

    role_data = {}
    role_data['id'] = role_result.id
    role_data['name'] = role_result.name

    return jsonify({'message': role_data})


# --------------------Resident management------------------------------#

#  add a resident [http://localhost/resident/add]
@app.route('/resident/add', methods=['POST'])
@token_required
def create_resident(current_user, role):
    data = request.get_json()
    room_check = Resident.query.filter_by(roomNumber=data['roomNumber']).first()
    if room_check:
        return make_response(jsonify({"message": "There's other resident in this room already!"}), 409)
    else:
        new_resident = Resident(name=data['name'].lower(), lineId=data['lineId'], roomNumber=data['roomNumber'])
        db.session.add(new_resident)
        db.session.commit()

        return make_response(jsonify({'message': 'new residents data created'}), 201)


# get all residents with pagination [http://localhost/resident/list?page=x]
@app.route('/resident/list', methods=['GET'])
@token_required
def get_residents(current_user, role):
    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    residents = Resident.query.order_by(Resident.id).all()

    total_pages = (len(residents) + per_page - 1) // per_page
    item_on_page = residents[start:end]

    output = []
    for resident in item_on_page:
        resident_data = {}
        resident_data['id'] = resident.id
        resident_data['name'] = resident.name
        resident_data['lineId'] = resident.lineId
        resident_data['roomNumber'] = resident.roomNumber

        output.append(resident_data)

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Resident': output})


# get a resident by id [http://localhost/resident/list/x]
@app.route('/resident/list/<res_id>', methods=['GET'])
@token_required
def get_resident(current_user, role, res_id):
    resident = Resident.query.filter_by(id=res_id).first()

    if not resident:
        return make_response(jsonify({"message": "The resident does not exist"}), 404)

    resident_data = {}
    resident_data['id'] = resident.id
    resident_data['name'] = resident.name
    resident_data['lineId'] = resident.lineId
    resident_data['roomNumber'] = resident.roomNumber

    return jsonify({'Resident': resident_data})


# get resident by room number for search [http://localhost/resident/list/room?query=x]
@app.route('/resident/list/room', methods=['GET'])
@token_required
def get_resident_by_roomNumber(current_user, role):
    query = request.args.get('query', type=str)

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    resident = Resident.query.filter_by(roomNumber=query).all()

    total_pages = (len(resident) + per_page - 1) // per_page
    item_on_page = resident[start:end]

    output = []

    if not resident:
        return make_response(jsonify({"message": "The resident with the room number does not exist"}), 404)

    else:
        for resident in item_on_page:
            resident_data = {}
            resident_data['id'] = resident.id
            resident_data['name'] = resident.name
            resident_data['lineId'] = resident.lineId
            resident_data['roomNumber'] = resident.roomNumber

            output.append(resident_data)

    page_data = {}
    page_data['total_pages'] = total_pages
    page_data['page'] = page
    output.append(page_data)
    return jsonify({'Resident': output})


# get resident by name for search [http://localhost/resident/list/name?query=x]
@app.route('/resident/list/name', methods=['GET'])
@token_required
def get_resident_by_name(current_user, role):
    query = request.args.get('query', type=str)

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    if not query:
        return jsonify([])

        # Adjust query for prefix matching
    query = ' & '.join([f"{word}:*" for word in query.split()])

    search_query = """
    SELECT * FROM Resident
    WHERE search_vector @@ to_tsquery(:search_term);
    """
    search_results = db.session.execute(text(search_query), {'search_term': query}).fetchall()

    total_pages = (len(search_results) + per_page - 1) // per_page
    item_on_page = search_results[start:end]

    output = []

    for resident in item_on_page:
        resident_data = {}
        resident_data['id'] = resident.id
        resident_data['name'] = resident.name
        resident_data['lineId'] = resident.lineId
        resident_data['roomNumber'] = resident.roomNumber

        output.append(resident_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'The resident with the name does not exist'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        output.append(page_data)
        return jsonify({'Resident': output})


# deleting a resident [http://localhost/resident/del/x]
@app.route('/resident/del/<res_id>', methods=['DELETE'])
@token_required
def delete_resident(current_user, role, res_id):
    resident = Resident.query.filter_by(id=res_id).first()
    if not resident:
        return make_response(jsonify({'message': 'The resident does not exist'}), 404)

    db.session.delete(resident)
    db.session.commit()
    return make_response(jsonify({'message': 'resident deleted'}), 202)


# update resident by id [http://localhost/resident/edit/x]
@app.route('/resident/edit/<res_id>', methods=['POST'])
@token_required
def update_resident(current_user, role, res_id):
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

            return make_response(jsonify({'message': 'Resident data has been update'}), 201)
    else:
        return make_response(jsonify({"message": "There's no resident exists!"}), 404)


# test today 28/05/2024
# --------------------Unit Record management------------------------------#

#  add a unit, [http://localhost/unit/add]
@app.route('/unit/add', methods=['POST'])
@token_required
def create_unit(current_user, role):
    data = request.get_json()

    try:
        new_unitRecord = Unit(numberOfUnits=data['numberOfUnits'],
                              date=date.datetime.now(),
                              extractionStatus=data['extractionStatus'],
                              approveStatus=False,
                              res_room=data['res_room'])
        db.session.add(new_unitRecord)
        db.session.commit()

        return make_response(jsonify({'message': 'new record created'}), 200)
    except:
        return make_response(jsonify({'message': 'The room that record refer does not exits!'}), 404)


# get record list by id [http://localhost/unit/list/x]
@app.route('/unit/list/<unit_id>', methods=['GET'])
@token_required
def get_unit(current_user, role, unit_id):
    unit_record = Unit.query.filter_by(id=unit_id).first()

    if not unit_record:
        return make_response(jsonify({'message': 'The record does not exist'}), 404)

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


# get record list by date [http://localhost/unit/list/date?page=x&start=%Y-%m-%d&end=%Y-%m-%d]
@app.route('/unit/list/date', methods=['GET'])
@token_required
def get_unit_by_date(current_user, role):
    startDate = request.args.get('start', type=toDate)
    endDate = request.args.get('end', type=toDate)

    # pagination
    page = request.args.get('page', type=int)

    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.filter(and_(Unit.date <= endDate, Unit.date >= startDate)).all()

    if not unit_record:
        return make_response(jsonify({'message': 'The record between the date does not exist'}), 404)

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
def get_unit_by_room(current_user, role):
    query = request.args.get('query', type=str)
    # pagination
    page = request.args.get('page', type=int)

    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.filter(Unit.res_room.like(query)).all()

    if not unit_record:
        return make_response(jsonify({'message': 'The record with the room number does not exist'}), 404)

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
def get_units(current_user, role):
    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page

    unit_record = Unit.query.order_by(Unit.id).all()

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
def delete_unit(current_user, role, rec_id):
    unit_record = Unit.query.filter_by(id=rec_id).first()
    if not unit_record:
        return make_response(jsonify({'message': 'record does not exist'}), 404)

    db.session.delete(unit_record)
    db.session.commit()
    return make_response(jsonify({'message': 'Record deleted'}), 200)


# update record [http://localhost/unit/edit/x]
@app.route('/unit/edit/<rec_id>', methods=['POST'])
@token_required
def update_unit(current_user, role, rec_id):
    date_format = '%Y-%m-%d'

    change_data = request.get_json()
    change_numberOfUnits = change_data['numberOfUnits']
    change_date = date.datetime.strptime(change_data['date'], date_format)
    change_extractionStatus = change_data['extractionStatus']
    change_approveStatus = change_data['approveStatus']
    change_room = change_data['res_room']

    unit_record = Unit.query.filter_by(id=rec_id).first()

    if unit_record:
        try:
            unit_record.numberOfUnits = change_numberOfUnits
            unit_record.date = change_date
            unit_record.extractionStatus = change_extractionStatus
            unit_record.approveStatus = change_approveStatus
            unit_record.res_room = change_room

            db.session.commit()
        except:
            return make_response(jsonify({"message": "The room that record refer does not exists!"}), 404)

        return make_response(jsonify({'message': 'Record data has been update'}), 200)
    else:
        return make_response(jsonify({"message": "There's no record exists!"}), 404)
