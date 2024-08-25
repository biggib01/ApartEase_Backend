from operator import and_
from flask import request, jsonify, make_response
import datetime as date
from library.main import db, app
from library.model.models import token_required, Unit
from library.functions import toDate, pagination
from library.model.models import UnitHistory  # Import the UnitHistory model

# --------------------Unit Record management------------------------------#

#  add a unit, [http://localhost/unit/add]
@app.route('/unit/add', methods=['POST'])
@token_required
def create_unit(current_user, role):
    data = request.get_json()

    try:
        new_unitRecord = Unit(
            numberOfUnits=data['numberOfUnits'],
            date=date.datetime.now(),
            extractionStatus=data['extractionStatus'],
            approveStatus=False,
            res_room=data['res_room'],
            costPerUnit=data.get('costPerUnit'),  # Add this line
            waterCost=data.get('waterCost'),      # Add this line
            rentCost=data.get('rentCost'),        # Add this line
   
        )
        db.session.add(new_unitRecord)
        db.session.commit()

        return make_response(jsonify({'message': 'new unit record created'}), 200)
    except Exception as e:
        print(f"Error creating unit: {e}")
        return make_response(jsonify({'message': 'The room that record refer does not exist!'}), 404)



# get record list by id [http://localhost/unit/list/x]
@app.route('/unit/list/<unit_id>', methods=['GET'])
@token_required
def get_unit(current_user, role, unit_id):
    unit_record = Unit.query.filter_by(id=unit_id).first()

    if not unit_record:
        return make_response(jsonify({'message': 'The unit does not exist'}), 404)

    record_data = {
        'id': unit_record.id,
        'numberOfUnits': unit_record.numberOfUnits,
        'date': unit_record.date,
        'extractionStatus': unit_record.extractionStatus,
        'approveStatus': unit_record.approveStatus,
        'res_room': unit_record.res_room,
        'costPerUnit': unit_record.costPerUnit,  # Add this line
        'waterCost': unit_record.waterCost,      # Add this line
        'rentCost': unit_record.rentCost,        # Add this line
 
    }

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
        record_data = {
            'id': record.id,
            'numberOfUnits': record.numberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'res_room': record.res_room,
            'costPerUnit': record.costPerUnit,  # Add this line
            'waterCost': record.waterCost,      # Add this line
            'rentCost': record.rentCost,        # Add this line
          
        }
        output.append(record_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_record': total_record
        }
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
        record_data = {
            'id': record.id,
            'numberOfUnits': record.numberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'res_room': record.res_room,
            'costPerUnit': record.costPerUnit,  # Add this line
            'waterCost': record.waterCost,      # Add this line
            'rentCost': record.rentCost,        # Add this line
       
        }
        output.append(record_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_record': total_record
        }
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
        record_data = {
            'id': record.id,
            'numberOfUnits': record.numberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'res_room': record.res_room,
            'costPerUnit': record.costPerUnit,  # Add this line
            'waterCost': record.waterCost,      # Add this line
            'rentCost': record.rentCost,        # Add this line
       
        }
        output.append(record_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no record data left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_record': total_record
        }
        output.append(page_data)
        return jsonify({'Unit': output})



# deleting a record [http://localhost/unit/del/x]
@app.route('/unit/del/<rec_id>', methods=['DELETE'])
@token_required
def delete_unit(current_user, role, rec_id):
    unit_record = Unit.query.filter_by(id=rec_id).first()
    if not unit_record:
        return make_response(jsonify({'message': 'Unit does not exist'}), 404)

    db.session.delete(unit_record)
    db.session.commit()
    return make_response(jsonify({'message': 'Unit deleted sucessfully!'}), 200)


# update record [http://localhost/unit/edit/x]
@app.route('/unit/edit/<rec_id>', methods=['PUT'])
@token_required
def update_unit(current_user, role, rec_id):
    change_data = request.get_json()

    unit_record = Unit.query.filter_by(id=rec_id).first()

    if unit_record:
        try:
            if 'numberOfUnits' in change_data:
                unit_record.numberOfUnits = change_data['numberOfUnits']
            if 'date' in change_data:
                unit_record.date = toDate(change_data['date'])
            if 'extractionStatus' in change_data:
                unit_record.extractionStatus = change_data['extractionStatus']
            if 'approveStatus' in change_data:
                unit_record.approveStatus = change_data['approveStatus']
            if 'res_room' in change_data:
                unit_record.res_room = change_data['res_room']
            if 'costPerUnit' in change_data:  # Add this block
                unit_record.costPerUnit = change_data['costPerUnit']
            if 'waterCost' in change_data:    # Add this block
                unit_record.waterCost = change_data['waterCost']
            if 'rentCost' in change_data:     # Add this block
                unit_record.rentCost = change_data['rentCost']
         

            db.session.commit()
            return make_response(jsonify({'message': 'Unit data has been updated'}), 200)
        except Exception as e:
            print(f"Error updating unit: {e}")
            return make_response(jsonify({"message": "The room that record refer does not exist!"}), 404)
    else:
        return make_response(jsonify({"message": "There's no unit exists!"}), 404)


