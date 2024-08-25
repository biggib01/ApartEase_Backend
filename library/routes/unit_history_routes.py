
from flask import request, jsonify, make_response
from library.main import db, app
from library.model.models import token_required, UnitHistory, Resident
from library.functions import pagination


@app.route('/unit/history/add', methods=['POST'])
@token_required
def add_unit_history(current_user, role):
    data = request.get_json()
    try:
        print(f"Received data: {data}")  # Log the received data

        # Check for missing required fields
        required_fields = ['numberOfUnits', 'extractionStatus', 'res_room', 'costPerUnit', 'waterCost', 'rentCost']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Convert approveStatus to boolean if provided
        approve_status = data.get('approveStatus', False)
        if isinstance(approve_status, str):
            approve_status = approve_status.lower() in ['true', '1', 'yes', 'approved']

        new_history = UnitHistory(
            numberOfUnits=data['numberOfUnits'],
            date=data.get('date'),  # Optional field
            extractionStatus=data['extractionStatus'],
            approveStatus=approve_status,
            res_room=data['res_room'],
            status='done',
            costPerUnit=data.get('costPerUnit'),  # Optional field
            waterCost=data.get('waterCost'),      # Optional field
            rentCost=data.get('rentCost'),        # Optional field
        )
        db.session.add(new_history)
        db.session.commit()
        return jsonify({'message': 'Unit history record added successfully!'})
    except KeyError as e:
        print(f"Missing key in data: {e}")  # Log the specific missing key
        return jsonify({'message': f'Missing key: {e}'}), 400
    except Exception as e:
        print(f"Error adding unit history: {e}")  # Log the error
        return jsonify({'message': f'Error adding unit history: {str(e)}'}), 500


@app.route('/unit/history/list', methods=['GET'])
@token_required
def get_unit_history(current_user, role):
    # Pagination
    page = request.args.get('page', 1, type=int)

    unit_history_records = UnitHistory.query.order_by(UnitHistory.id).all()

    total_records = len(unit_history_records)

    if not unit_history_records:
        return make_response(jsonify({"message": "There is no unit history data yet!"}), 404)

    total_pages, item_on_page = pagination(page, unit_history_records, 5)

    output = []
    for record in item_on_page:
        record_data = {
            'id': record.id,
            'numberOfUnits': record.numberOfUnits,
            'date': record.date,
            'extractionStatus': record.extractionStatus,
            'approveStatus': record.approveStatus,
            'res_room': record.res_room,
            'status': record.status,
            'costPerUnit': record.costPerUnit,
            'waterCost': record.waterCost,
            'rentCost': record.rentCost,
        }
        output.append(record_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no unit history data left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_records': total_records
        }
        output.append(page_data)
        return jsonify({'UnitHistory': output})


@app.route('/unit/history/edit/<int:id>', methods=['PUT'])
@token_required
def update_unit_history(current_user, role, id):
    data = request.get_json()
    try:
        unit_history = UnitHistory.query.get(id)
        if not unit_history:
            return jsonify({'message': 'Unit history record not found'}), 404

        unit_history.numberOfUnits = data.get('numberOfUnits', unit_history.numberOfUnits)
        unit_history.date = data.get('date', unit_history.date)
        unit_history.extractionStatus = data.get('extractionStatus', unit_history.extractionStatus)
        unit_history.approveStatus = data.get('approveStatus', unit_history.approveStatus)
        unit_history.res_room = data.get('res_room', unit_history.res_room)
        unit_history.status = data.get('status', unit_history.status)
        unit_history.costPerUnit = data.get('costPerUnit', unit_history.costPerUnit)
        unit_history.waterCost = data.get('waterCost', unit_history.waterCost)
        unit_history.rentCost = data.get('rentCost', unit_history.rentCost)

        db.session.commit()
        return jsonify({'message': 'Unit history record updated successfully!'})
    except Exception as e:
        print(f"Error updating unit history: {e}")  # Log the error
        return jsonify({'message': 'Error updating unit history'}), 500


@app.route('/unit/history/del/<int:id>', methods=['DELETE'])
@token_required
def delete_unit_history(current_user, role, id):
    try:
        unit_history = UnitHistory.query.get(id)
        if not unit_history:
            return jsonify({'message': 'Unit history record not found'}), 404

        db.session.delete(unit_history)
        db.session.commit()
        return jsonify({'message': 'Unit history record deleted successfully!'})
    except Exception as e:
        print(f"Error deleting unit history: {e}")  # Log the error
        return jsonify({'message': 'Error deleting unit history'}), 500


@app.route('/unit/history/detail/<int:id>', methods=['GET'])
@token_required
def get_unit_history_detail(current_user, role, id):
    try:
        unit_history = UnitHistory.query.get(id)
        if not unit_history:
            return jsonify({'message': 'Unit history record not found'}), 404

        # Fetch the resident details
        resident = Resident.query.filter_by(roomNumber=unit_history.res_room).first()

        if not resident:
            print(f"No resident found for room number: {unit_history.res_room}")

        detail_data = {
            'id': unit_history.id,
            'numberOfUnits': unit_history.numberOfUnits,
            'date': str(unit_history.date),  # Convert date to string
            'extractionStatus': unit_history.extractionStatus,
            'approveStatus': unit_history.approveStatus,
            'res_room': unit_history.res_room,
            'status': unit_history.status,
            'costPerUnit': float(unit_history.costPerUnit),  # Convert to float
            'waterCost': float(unit_history.waterCost),  # Convert to float
            'rentCost': float(unit_history.rentCost),  # Convert to float
            'residentName': resident.name if resident else None,
            'residentEmail': resident.lineId if resident else None  # Use lineId as email
        }

        return jsonify({'UnitHistoryDetail': detail_data})
    except Exception as e:
        print(f"Error fetching unit history detail: {e}")  # Log the error
        return jsonify({'message': f'Error fetching unit history detail: {str(e)}'}), 500
