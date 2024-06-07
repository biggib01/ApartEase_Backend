from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash
from library.functions import pagination
from library.main import db, app
from library.model.models import Users, token_required, Roles

# --------------------User management------------------------------#

# register route [http://localhost/user/add]
@app.route('/user/add', methods=['POST'])
@token_required
def create_user(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

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


# edit user's info [http://localhost/user/edit/x]
@app.route('/user/edit/<uid>', methods=['POST'])
@token_required
def edit_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    change_data = request.get_json()
    change_username = change_data['username']
    change_password = generate_password_hash(change_data['password'], method='sha256')
    change_role = change_data['role']

    user = Users.query.filter_by(id=uid).first()

    if user:
        user.username = change_username
        user.password = change_password

        role = Roles.query.filter_by(name=change_role).first()

        if not role:
            return make_response(jsonify({"message": "The role dose not exists"}), 404)

        user.roles.append(role)

        db.session.commit()

        return make_response(jsonify({'message': 'User data has been update'}), 200)
    else:
        return make_response(jsonify({"message": "There's no user exists!"}), 404)


# get all users [http://localhost/user/list]
@app.route('/user/list', methods=['GET'])
@token_required
def get_users(current_user, role):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    # pagination
    page = request.args.get('page', 1, type=int)

    users = Users.query.order_by(Users.id).all()

    if not users:
        return make_response(jsonify({"message": "There is no user data yet!"}), 404)

    total_pages, item_on_page = pagination(page, users, 5)

    output = []
    for user in item_on_page:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username

        role_list = []

        for role in user.roles:
            role_data = {}
            role_data['name'] = role.name

            role_list.append(role_data)

        user_data['has_admin_role'] = role_list

        output.append(user_data)

    if len(output) == 0:
        return make_response(jsonify({'message': 'There is no user data left!'}), 404)
    else:
        page_data = {}
        page_data['total_pages'] = total_pages
        page_data['page'] = page
        output.append(page_data)
        return jsonify({'User': output})


# get user by id [http://localhost/user/list/x]
@app.route('/user/list/<uid>', methods=['GET'])
@token_required
def get_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    user = Users.query.filter_by(id=uid).first()

    if not user:
        return make_response(jsonify({'message': 'user does not exist'}), 404)

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    role_list = []

    for role in user.roles:
        role_data = {}
        role_data['name'] = role.name

        role_list.append(role_data)

    user_data['has_admin_role'] = role_list

    return jsonify({'User': user_data})


# deleting a user [http://localhost/user/del/x]
@app.route('/user/del/<uid>', methods=['DELETE'])
@token_required
def delete_user(current_user, role, uid):
    # role check
    if role != "admin":
        return make_response(jsonify({'message': 'access denied'}), 401)

    user = Users.query.filter_by(id=uid).first()
    if not user:
        return make_response(jsonify({'message': 'User does not exist'}), 404)

    db.session.delete(user)
    db.session.commit()
    return make_response(jsonify({'message': 'User deleted'}), 200)

