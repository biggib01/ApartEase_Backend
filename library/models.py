from sqlalchemy.orm import backref
from flask import request, jsonify, make_response
from library.main import app, db
from functools import wraps
import jwt
from flask_restful import abort


# users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return '<User {}>'.format(self.username)

# token decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # pass jwt-token in headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: # throw error if no token provided
            return make_response(jsonify({"message": "A valid token is missing!"}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return make_response(jsonify({"message": "Invalid token!"}), 401)

        return f(current_user, *args, **kwargs)
    return decorator

# resident table
class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lineId = db.Column(db.String)
    roomNumber = db.Column(db.String, nullable=False, unique=True)
    unit = db.relationship('Unit', backref='resident')

    def __repr__(self):
        return f'<Resident "{self.title}">'

# unit from meter OCR table
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numberOfUnits = db.Column(db.Integer)
    date = db.Column(db.Date)
    extractionStatus = db.Column(db.String)
    approveStatus = db.Column(db.Boolean)
    res_room = db.Column(db.String, db.ForeignKey('resident.roomNumber'))

    def __repr__(self):
        return f'<Unit "{self.title}">'