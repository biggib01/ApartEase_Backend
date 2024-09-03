from flask import request, jsonify, make_response
from library.main import db, app
from library.model.models import token_required, BillHistory, Resident, Unit, Bill
from library.functions import pagination, toDate


@app.route('/bill/history/add', methods=['POST'])
@token_required
def add_bill_history(current_user, role):
    data = request.get_json()

    # Ensure data is either a list or a single dictionary
    if not isinstance(data, (list, dict)):
        return jsonify({'message': 'Data should be a list or a single bill history record'}), 400

    # If data is a single dictionary, convert it to a list
    if isinstance(data, dict):
        data = [data]

    try:
        for record in data:
            print(f"Received data: {record}")  # Log the received data

            # Check for missing required fields
            required_fields = ['unit_id', 'amount', 'date_sent']
            missing_fields = [field for field in required_fields if field not in record]
            if missing_fields:
                return jsonify({'message': f'Missing required fields in one of the records: {", ".join(missing_fields)}'}), 400

            # Check if the unit_id exists in the Unit table
            unit = Unit.query.get(record['unit_id'])
            if not unit:
                return jsonify({'message': f'The specified unit_id {record["unit_id"]} does not exist in the Unit table'}), 400

            # Check if a bill history record already exists for the given unit_id and date_sent
            existing_history = BillHistory.query.filter_by(unit_id=record['unit_id'], date_sent=toDate(record['date_sent'])).first()
            if existing_history:
                existing_history.amount = record['amount']
            else:
                new_history = BillHistory(
                    unit_id=record['unit_id'],
                    amount=record['amount'],
                    date_sent=toDate(record['date_sent'])
                )
                db.session.add(new_history)

        db.session.commit()
        return jsonify({'message': 'Bill history records processed successfully!'})
    except KeyError as e:
        print(f"Missing key in data: {e}")  # Log the specific missing key
        return jsonify({'message': f'Missing key: {e}'}), 400
    except Exception as e:
        print(f"Error adding bill history: {e}")  # Log the error
        return jsonify({'message': f'Error adding bill history: {str(e)}'}), 400






@app.route('/bill/history/list', methods=['GET'])
@token_required
def get_bill_history(current_user, role):
    # Pagination
    page = request.args.get('page', 1, type=int)

    bill_history_records = BillHistory.query.order_by(BillHistory.id).all()

    total_records = len(bill_history_records)

    if not bill_history_records:
        return make_response(jsonify({"message": "There is no bill history data yet!"}), 404)

    total_pages, item_on_page = pagination(page, bill_history_records, 5)

    output = []
    for record in item_on_page:
        record_data = {
            'id': record.id,
            'unit_id': record.unit_id,
            'amount': record.amount,
            'date_sent': record.date_sent,
            'res_room': record.res_room  # Include the room number
        }
        output.append(record_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no bill history data left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_records': total_records
        }
        output.append(page_data)
        return jsonify({'BillHistory': output})



@app.route('/bill/history/date', methods=['GET'])
@token_required
def get_bill_history_by_date(current_user, role):
    startDate = request.args.get('start', type=toDate)
    endDate = request.args.get('end', type=toDate)

    # Pagination
    page = request.args.get('page', 1, type=int)

    bill_history_records = BillHistory.query.filter(BillHistory.date_sent.between(startDate, endDate)).all()

    if not bill_history_records:
        return make_response(jsonify({'message': 'The record between the date does not exist'}), 404)

    total_record = len(bill_history_records)
    total_pages, item_on_page = pagination(page, bill_history_records, 5)

    output = []
    for record in item_on_page:
        record_data = {
            'id': record.id,
            'unit_id': record.unit_id,
            'amount': record.amount,
            'date_sent': record.date_sent
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
        return jsonify({'BillHistory': output})


@app.route('/bill/history/edit/<int:id>', methods=['PUT'])
@token_required
def update_bill_history(current_user, role, id):
    data = request.get_json()
    try:
        print(f"Updating BillHistory with ID: {id}")  # Log the ID being queried
        bill_history = BillHistory.query.get(id)
        if not bill_history:
            print(f"BillHistory with ID {id} not found")  # Log if the record is not found
            return jsonify({'message': 'Bill history record not found'}), 404

        bill_history.amount = data.get('amount', bill_history.amount)
        bill_history.date_sent = toDate(data.get('date_sent', bill_history.date_sent))

        db.session.commit()
        return jsonify({'message': 'Bill history record updated successfully!'})
    except Exception as e:
        print(f"Error updating bill history: {e}")  # Log the error
        return jsonify({'message': 'Error updating bill history'}), 500



@app.route('/bill/history/del/<int:id>', methods=['DELETE'])
@token_required
def delete_bill_history(current_user, role, id):
    try:
        bill_history = BillHistory.query.get(id)
        if not bill_history:
            return jsonify({'message': 'Bill history record not found'}), 404

        db.session.delete(bill_history)
        db.session.commit()
        return jsonify({'message': 'Bill history record deleted successfully!'})
    except Exception as e:
        print(f"Error deleting bill history: {e}")  # Log the error
        return jsonify({'message': 'Error deleting bill history'}), 500
    


# Delete all bill history records [http://localhost/bill/history/del_all]
@app.route('/bill/history/del_all', methods=['DELETE'])
@token_required
def delete_all_bill_history(current_user, role):
    try:
        # Fetch all bill history records
        bill_histories = BillHistory.query.all()
        if not bill_histories:
            return make_response(jsonify({'message': 'No bill history records found'}), 404)

        # Delete all bill history records
        for bill_history in bill_histories:
            db.session.delete(bill_history)
        db.session.commit()

        return make_response(jsonify({'message': 'All bill history records deleted successfully'}), 200)
    except Exception as e:
        print(f"Error deleting all bill history records: {e}")
        return make_response(jsonify({'message': 'Error deleting all bill history records', 'error': str(e)}), 500)    


@app.route('/bill/history/<int:id>', methods=['GET'])
@token_required
def get_bill_history_detail(current_user, role, id):
    try:
        bill_history = BillHistory.query.get(id)
        if not bill_history:
            return jsonify({'message': 'Bill history record not found'}), 404

        # Fetch the resident details
        resident = Resident.query.filter_by(roomNumber=bill_history.unit.res_room).first()

        if not resident:
            print(f"No resident found for room number: {bill_history.unit.res_room}")

        detail_data = {
            'id': bill_history.id,
            'unit_id': bill_history.unit_id,
            'amount': bill_history.amount,
            'date_sent': str(bill_history.date_sent),  # Convert date to string
        }

        return jsonify({'BillHistoryDetail': detail_data})
    except Exception as e:
        print(f"Error fetching bill history detail: {e}")  # Log the error
        return jsonify({'message': f'Error fetching bill history detail: {str(e)}'}), 500
