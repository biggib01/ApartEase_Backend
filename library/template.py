from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid
from datetime import datetime, timedelta
from library.main import db, app
from library.models import User, token_required, Resident, Unit


#  add a resident
@app.route('/resident/add', methods=['POST'])
@token_required
def create_resident(current_user):
    '''adds a new book to collection!'''
    data = request.get_json()
    room_check = Resident.query.filter_by(title=data['roomNumber']).first()
    if room_check:
        return make_response(jsonify({"message": "There's other resident in this room already!"}), 409)
    else:
        resident = Resident.query.filter_by(title=data['name']).first()
        if resident:
            return make_response(jsonify({"message": "Resident with same name already exists!"}), 409)
        else:
            new_resident = Resident(name=data['name'], lineId=data['lineId'], roomNumber=data['roomNumber'])
            db.session.add(new_resident)
            db.session.commit()

            return jsonify({'message' : 'new residents data created'})


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
        resident_data['unitList'] = resident.unit
        output.append(resident_data)

    return jsonify({'Resident': output})
