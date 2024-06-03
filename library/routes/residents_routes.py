from flask import request, jsonify, make_response
from sqlalchemy import text
from library.main import db, app
from library.model.models import token_required, Resident
from library.functions import pagination

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

    resident = Resident.query.order_by(Resident.id).all()

    total_resident = len(resident)

    if not resident:
        return make_response(jsonify({"message": "There is no residents data yet!"}), 404)

    total_pages, item_on_page = pagination(page, resident, 5)

    output = []
    for resident in item_on_page:
        resident_data = {}
        resident_data['id'] = resident.id
        resident_data['name'] = resident.name
        resident_data['lineId'] = resident.lineId
        resident_data['roomNumber'] = resident.roomNumber

        output.append(resident_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no residents data left!'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        page_data['total_resident'] = total_resident
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
    page = request.args.get('page', 1, type=int)

    resident = Resident.query.filter_by(roomNumber=query).all()

    total_pages, item_on_page = pagination(page, resident, 5)

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

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no residents data left!'}), 404)
    else:
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

    if not query:
        return jsonify([])

        # Adjust query for prefix matching
    query = ' & '.join([f"{word}:*" for word in query.split()])

    search_query = """
    SELECT * FROM Resident
    WHERE search_vector @@ to_tsquery(:search_term);
    """
    resident = db.session.execute(text(search_query), {'search_term': query}).fetchall()

    if not resident:
        return make_response(jsonify({"message": "The resident with the name does not exist"}), 404)

    total_pages, item_on_page = pagination(page, resident, 5)

    output = []

    for resident in item_on_page:
        resident_data = {}
        resident_data['id'] = resident.id
        resident_data['name'] = resident.name
        resident_data['lineId'] = resident.lineId
        resident_data['roomNumber'] = resident.roomNumber

        output.append(resident_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no residents data left!'}), 404)
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
