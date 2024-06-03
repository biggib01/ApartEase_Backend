from flask import request, jsonify, make_response
from werkzeug.security import check_password_hash
import jwt
from library.main import app
from library.model.models import Users

# --------------------Authentication------------------------------#

# user login route [http://localhost/login]
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = Users.query.filter_by(username=auth['username']).first()
    if not user:
        return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        token = jwt.encode({'username': user.username}, app.config['SECRET_KEY'], 'HS256')

        role_output = []

        for role in user.roles:
            role_data = {}
            role_data['name'] = role.name

            role_output.append(role_data)

        user_data = {'username': user.username, 'role': role_output, 'token': token}
        return make_response(jsonify({'User': user_data}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})
