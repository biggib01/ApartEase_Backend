from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash
from library.main import db, app
from library.model.models import Users, token_required, Roles

# --------------------User management------------------------------#

# register route [http://localhost/dev/user/add]
@app.route('/dev/user/add', methods=['POST'])
def dev_create_user():

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


#  add a role, [http://localhost/dev/role/add]
@app.route('/dev/role/add', methods=['POST'])
def dev_create_role():
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

