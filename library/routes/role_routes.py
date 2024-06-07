from flask import request, jsonify, make_response
from library.main import db, app
from library.model.models import token_required, Roles

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

    return jsonify({'Role': output})


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

    return jsonify({'Role': role_data})

