from operator import and_
from flask import request, jsonify, make_response
import datetime as date
from library.main import db, app
from library.model.models import token_required, Unit
from library.functions import toDate, pagination

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


# get record list by date [http://localhost/unit/list/date?page=x&start=%Y-%m-%d&end=%Y-%m-%d]
@app.route('/unit/list/date', methods=['GET'])
@token_required
def get_unit_by_date(current_user, role):
    startDate = request.args.get('start', type=toDate)
    endDate = request.args.get('end', type=toDate)

    # pagination
    page = request.args.get('page', 1, type=int)

    unit_record = Unit.query.filter(and_(Unit.date <= endDate, Unit.date >= startDate)).all()

    if not unit_record:
        return make_response(jsonify({'message': 'The record between the date does not exist'}), 404)

    total_record = len(unit_record)

    total_pages, item_on_page = pagination(page, unit_record, 5)

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

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        page_data['total_record'] = total_record
        output.append(page_data)
        return jsonify({'Unit': output})


# get record list by room number [http://localhost/unit/list/room?page=x&query=x]
@app.route('/unit/list/room', methods=['GET'])
@token_required
def get_unit_by_room(current_user, role):
    query = request.args.get('query', type=str)
    # pagination
    page = request.args.get('page', 1, type=int)

    unit_record = Unit.query.filter(Unit.res_room.like(query)).all()

    if not unit_record:
        return make_response(jsonify({'message': 'The record with the room number does not exist'}), 404)

    total_record = len(unit_record)

    total_pages, item_on_page = pagination(page, unit_record, 5)

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

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        page_data['total_record'] = total_record
        output.append(page_data)
        return jsonify({'Unit': output})


# get all records with pagination [http://localhost/unit/list]
@app.route('/unit/list', methods=['GET'])
@token_required
def get_units(current_user, role):
    # pagination
    page = request.args.get('page', 1, type=int)

    unit_record = Unit.query.order_by(Unit.id).all()

    if not unit_record:
        return make_response(jsonify({"message": "There is no record data yet!"}), 404)

    total_record = len(unit_record)

    total_pages, item_on_page = pagination(page, unit_record, 5)

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

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        page_data['total_record'] = total_record
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
    change_date = toDate(change_data['date'])
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
