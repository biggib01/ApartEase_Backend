from flask import request, jsonify, make_response
from library.main import db, app
from library.model.models import token_required, Bill, Resident, Unit
from library.functions import pagination, toDate
from flask_mail import Message
from library.main import mail


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------Bill Management------------------------------#

@app.route('/bill/send/<bill_id>', methods=['POST'])
@token_required
def send_bill_by_email(current_user, role, bill_id):
    # Fetch the bill details
    bill = Bill.query.filter_by(id=bill_id).first()
    if not bill:
        return make_response(jsonify({'message': 'Bill does not exist'}), 404)

    # Fetch the resident details associated with the bill
    resident = Resident.query.filter_by(roomNumber=bill.res_room).first()
    if not resident:
        return make_response(jsonify({'message': 'Resident does not exist'}), 404)

    # Create the email content
    subject = f"Bill Details for Bill ID: {bill.id}"
    body = f"""
    Dear {resident.name},

    Here are the details of your bill:

    Bill Details:
    ------------
    Bill ID: {bill.id}
    Date: {bill.date}
    Room: {bill.res_room}

    Charges:
    --------
    Rent: ฿{bill.rentCost:.2f}
    Water: ฿{bill.waterCost:.2f}
    Electricity:
        Total Units: {bill.totalUnit}
        Cost Per Unit: ฿{bill.costPerUnit:.2f}
        Total Electricity Cost: ฿{bill.totalUnit * bill.costPerUnit:.2f}

    Total Bill: ฿{bill.totalBill:.2f}
    Thank you.
    """

    # Create the email message
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[resident.lineId])
    msg.body = body

    try:
        # Send the email
        mail.send(msg)
        return make_response(jsonify({'message': 'Bill sent successfully'}), 200)
    except Exception as e:
        print(f"Error sending email: {e}")
        return make_response(jsonify({'message': 'Failed to send bill', 'error': str(e)}), 500)
    

@app.route('/bill/send_all', methods=['POST'])
@token_required
def send_all_bills(current_user, role):
    try:
        # Fetch all bills
        bills = Bill.query.all()
        if not bills:
            return make_response(jsonify({'message': 'No bills found'}), 404)

        for bill in bills:
            # Fetch the resident details associated with the bill
            resident = Resident.query.filter_by(roomNumber=bill.res_room).first()
            if not resident:
                continue  # Skip if no resident found for the bill

            # Create the email content
            subject = f"Bill Details for Bill ID: {bill.id}"
            body = f"""
            Dear {resident.name},

            Here are the details of your bill:

            Bill Details:
            ------------
            Bill ID: {bill.id}
            Date: {bill.date}
            Room: {bill.res_room}

            
            Charges:
            --------
            Rent: ฿{bill.rentCost:.2f}
            Water: ฿{bill.waterCost:.2f}
            Electricity:
                Total Units: {bill.totalUnit}
                Cost Per Unit: ฿{bill.costPerUnit:.2f}
                Total Electricity Cost: ฿{bill.totalUnit * bill.costPerUnit:.2f}

                Total Bill: ฿{bill.totalBill:.2f}
                Thank you.
                """

            # Create the email message
            msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[resident.lineId])
            msg.body = body

            try:
                # Send the email
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email to {resident.lineId}: {e}")

        return make_response(jsonify({'message': 'All bills sent successfully'}), 200)
    except Exception as e:
        print(f"Error sending all bills: {e}")
        return make_response(jsonify({'message': 'Failed to send all bills', 'error': str(e)}), 500)

        
# Add a bill [http://localhost/bill/add]
@app.route('/bill/add', methods=['POST'])
@token_required
def create_bill(current_user, role):
    data = request.get_json()

    try:
        new_bill = Bill(
            date=toDate(data['date']),
            res_room=data['res_room'],
            totalUnit=data['totalUnit'],
            totalBill=data['totalBill'],
            waterCost=data.get('waterCost', 0.0),
            rentCost=data.get('rentCost', 0.0),
            costPerUnit=data.get('costPerUnit', 0.0)
        )
        db.session.add(new_bill)
        db.session.commit()

        return make_response(jsonify({'message': 'New bill created'}), 200)
    except Exception as e:
        print(f"Error creating bill: {e}")
        return make_response(jsonify({'message': 'Error creating bill'}), 500)


# Get all bills with pagination [http://localhost/bill/list]
@app.route('/bill/list', methods=['GET'])
@token_required
def get_bills(current_user, role):
    # pagination
    page = request.args.get('page', 1, type=int)

    bills = Bill.query.order_by(Bill.id).all()

    if not bills:
        return make_response(jsonify({"message": "There are no bills yet!"}), 404)

    total_bills = len(bills)

    total_pages, item_on_page = pagination(page, bills, 5)

    output = []
    for bill in item_on_page:
        bill_data = {
            'id': bill.id,
            'date': bill.date,
            'res_room': bill.res_room,
            'totalUnit': bill.totalUnit,
            'totalBill': bill.totalBill,
            'waterCost': bill.waterCost,
            'rentCost': bill.rentCost,
            'costPerUnit': bill.costPerUnit
            
        }
        output.append(bill_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There are no bills left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_bills': total_bills
        }
        output.append(page_data)
        return jsonify({'Bills': output})


# Get bills by room number [http://localhost/bill/list/room?query=x&page=x]
@app.route('/bill/list/room', methods=['GET'])
@token_required
def get_bills_by_room(current_user, role):
    query = request.args.get('query', type=str)
    page = request.args.get('page', 1, type=int)

    bills = Bill.query.filter(Bill.res_room.like(query)).all()

    if not bills:
        return make_response(jsonify({'message': 'No bills found for the specified room'}), 404)

    total_bills = len(bills)

    total_pages, item_on_page = pagination(page, bills, 5)

    output = []
    for bill in item_on_page:
        bill_data = {
            'id': bill.id,
            'date': bill.date,
            'res_room': bill.res_room,
            'totalUnit': bill.totalUnit,
            'totalBill': bill.totalBill,
            'waterCost': bill.waterCost,
            'rentCost': bill.rentCost,
            'costPerUnit': bill.costPerUnit
        }
        output.append(bill_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There are no bills left!'}), 404)
    else:
        page_data = {
            'total_pages': total_pages,
            'page': page,
            'total_bills': total_bills
        }
        output.append(page_data)
        return jsonify({'Bills': output})

# Delete a bill by id [http://localhost/bill/del/<bill_id>]
@app.route('/bill/del/<bill_id>', methods=['DELETE'])
@token_required
def delete_bill(current_user, role, bill_id):
    # Check if the bill exists
    bill = Bill.query.filter_by(id=bill_id).first()
    if not bill:
        return make_response(jsonify({'message': 'Bill does not exist'}), 404)

    # Delete the bill
    db.session.delete(bill)
    db.session.commit()
    return make_response(jsonify({'message': 'Bill deleted'}), 200)


# Update a bill by id [http://localhost/bill/edit/<bill_id>]
@app.route('/bill/edit/<bill_id>', methods=['PUT'])
@token_required
def update_bill(current_user, role, bill_id):
    data = request.get_json()

    # Fetch the bill details
    bill = Bill.query.filter_by(id=bill_id).first()
    if not bill:
        return make_response(jsonify({'message': 'Bill does not exist'}), 404)

    try:
        # Update the bill details
        if 'date' in data:
            bill.date = toDate(data['date'])
        if 'res_room' in data:
            bill.res_room = data['res_room']
        if 'totalUnit' in data:
            bill.totalUnit = data['totalUnit']
        if 'totalBill' in data:
            bill.totalBill = data['totalBill']
        if 'waterCost' in data:
            bill.waterCost = data['waterCost']
        if 'rentCost' in data:
            bill.rentCost = data['rentCost']
        if 'costPerUnit' in data:
            bill.costPerUnit = data['costPerUnit']


        db.session.commit()

        return make_response(jsonify({'message': 'Bill updated successfully'}), 200)
    except Exception as e:
        print(f"Error updating bill: {e}")
        return make_response(jsonify({'message': 'Error updating bill', 'error': str(e)}), 500)
