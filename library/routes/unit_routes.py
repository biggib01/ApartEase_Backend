import os
from operator import and_
from flask import request, jsonify, make_response
import datetime as date
from library.main import db, app
from library.model.models import token_required, Unit
from library.functions import toDate, pagination
from azblobexplorer import AzureBlobDelete
from dotenv import load_dotenv

load_dotenv()

# --------------------Unit Record management------------------------------#

# add a unit, [http://localhost/unit/add]
@app.route('/unit/add', methods=['POST'])
def create_or_update_unit():
    data = request.get_json()

    try:
        extraction_status = data['extractionStatus']
        approve_status = True if extraction_status == 'Fully successful' else False if extraction_status == 'Not fully successful' else False
        res_room = data['res_room']
        number_of_units = data['numberOfUnits']
        imgUrl = data['imgUrl']

        # Check if a unit record already exists for the given room number
        existing_unit = Unit.query.filter_by(res_room=res_room).first()

        if existing_unit:
            # Update the existing unit record
            existing_unit.prevNumberOfUnits = existing_unit.numberOfUnits
            existing_unit.numberOfUnits = number_of_units
            existing_unit.date = date.datetime.now()
            existing_unit.extractionStatus = extraction_status
            existing_unit.imgUrl = imgUrl
            existing_unit.approveStatus = approve_status
        else:
            # Create a new unit record with prevNumberOfUnits set to 0
            new_unitRecord = Unit(
                numberOfUnits=number_of_units,
                prevNumberOfUnits='0',
                date=date.datetime.now(),
                extractionStatus=extraction_status,
                approveStatus=approve_status,
                imgUrl=imgUrl,
                res_room=res_room
            )
            db.session.add(new_unitRecord)

        db.session.commit()

        return make_response(jsonify({'message': 'Unit record processed successfully'}), 200)
    except Exception as e:
        print(f"Error processing unit: {e}")
        return make_response(jsonify({'message': 'The room that record refers to does not exist!'}), 404)




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
        'prevNumberOfUnits': unit_record.prevNumberOfUnits,
        'date': unit_record.date,
        'extractionStatus': unit_record.extractionStatus,
        'approveStatus': unit_record.approveStatus,
        'imgUrl': unit_record.imgUrl,
        'res_room': unit_record.res_room
    }

    return jsonify({'Unit': record_data})


# # get record list by date [http://localhost/unit/list/date?page=x&start=%Y-%m-%d&end=%Y-%m-%d]
# @app.route('/unit/list/date', methods=['GET'])
# @token_required
# def get_unit_by_date(current_user, role):
#     startDate = request.args.get('start', type=toDate)
#     endDate = request.args.get('end', type=toDate)

#     # pagination
#     page = request.args.get('page', 1, type=int)

#     unit_record = Unit.query.filter(and_(Unit.date <= endDate, Unit.date >= startDate)).all()

#     if not unit_record:
#         return make_response(jsonify({'message': 'The record between the date does not exist'}), 404)

#     total_record = len(unit_record)
#     total_pages, item_on_page = pagination(page, unit_record, 5)

#     output = []
#     for record in item_on_page:
#         record_data = {
#             'id': record.id,
#             'numberOfUnits': record.numberOfUnits,
#             'prevNumberOfUnits': record.prevNumberOfUnits,
#             'date': record.date,
#             'extractionStatus': record.extractionStatus,
#             'approveStatus': record.approveStatus,
#             'res_room': record.res_room
#         }
#         output.append(record_data)

#     if len(output) == 0:
#         return make_response(jsonify({'message': 'There is no record data left!'}), 404)
#     else:
#         page_data = {
#             'total_pages': total_pages,
#             'page': page,
#             'total_record': total_record
#         }
#         output.append(page_data)
#         return jsonify({'Unit': output})


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
            'prevNumberOfUnits': record.prevNumberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'imgUrl': record.imgUrl,
            'res_room': record.res_room
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
            'prevNumberOfUnits': record.prevNumberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'imgUrl': record.imgUrl,
            'res_room': record.res_room
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

    accountName = os.getenv('AZURE_ACCOUNT_NAME')
    accountKey = os.getenv('AZURE_ACCOUNT_KEY')
    containerName = os.getenv('CONTAINER_NAME')

    az = AzureBlobDelete(accountName, accountKey, containerName)

    url = unit_record.imgUrl

    filename = url.rsplit('/', 1)[-1]
    print(filename)

    az.delete_file(filename)


    db.session.delete(unit_record)
    db.session.commit()
    return make_response(jsonify({'message': 'Unit deleted successfully!'}), 200)


# update record [http://localhost/unit/edit/x]
@app.route('/unit/edit/<rec_id>', methods=['PUT'])
@token_required
def update_unit(current_user, role, rec_id):
    change_data = request.get_json()

    unit_record = Unit.query.filter_by(id=rec_id).first()

    if unit_record:
        try:
            if 'numberOfUnits' in change_data:
                # Copy current numberOfUnits to prevNumberOfUnits before updating
                unit_record.numberOfUnits = change_data['numberOfUnits']
            if 'extractionStatus' in change_data:
                unit_record.extractionStatus = change_data['extractionStatus']
                unit_record.approveStatus = True if unit_record.extractionStatus == 'Fully successful' else False if unit_record.extractionStatus == 'Not fully successful' else False
            if 'prevNumberOfUnits' in change_data:
                unit_record.prevNumberOfUnits = change_data['prevNumberOfUnits']
            if 'date' in change_data:
                unit_record.date = change_data['date']
            if 'imgUrl' in change_data:
                unit_record.imgUrl = change_data['imgUrl']
            if 'res_room' in change_data:
                unit_record.res_room = change_data['res_room']

            db.session.commit()
            return make_response(jsonify({'message': 'Unit data has been updated'}), 200)
        except Exception as e:
            print(f"Error updating unit: {e}")
            return make_response(jsonify({"message": "Error updating unit data!"}), 404)
    else:
        return make_response(jsonify({"message": "There's no unit exists!"}), 404)



