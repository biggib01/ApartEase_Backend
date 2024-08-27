from flask import request, jsonify, make_response
from library.main import app, db
from functools import wraps
import jwt
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.event import listen
from sqlalchemy import text


# users table
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))

    roles = db.relationship('Roles', secondary='user_roles')

    def __repr__(self):
        return '<User {}>'.format(self.username)


# roles table
class Roles(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# mapping table between user and role
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# resident table
class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    lineId = db.Column(db.String)
    roomNumber = db.Column(db.String, nullable=False, unique=True)
    unit = db.relationship('Unit', backref='resident')
    search_vector = db.Column(TSVECTOR)

    __table_args__ = (
        db.Index('ix_resident_search_vector', 'search_vector', postgresql_using='gin'),
    )

    def __repr__(self):
        return f'<Resident "{self.name}">'


class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numberOfUnits = db.Column(db.String)
    prevNumberOfUnits = db.Column(db.String)
    date = db.Column(db.Date)
    extractionStatus = db.Column(db.String)
    approveStatus = db.Column(db.Boolean)
    res_room = db.Column(db.String, db.ForeignKey('resident.roomNumber'))

    @property
    def total_units(self):
        if self.prevNumberOfUnits and self.numberOfUnits:
            return int(self.numberOfUnits) - int(self.prevNumberOfUnits)
        return None

    def update_prev_units(self):
        """Update the previous month's units with the current month's units."""
        self.prevNumberOfUnits = self.numberOfUnits


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    amount = db.Column(db.Float)
    date_created = db.Column(db.Date)
    is_sent = db.Column(db.Boolean, default=False)
    unit = db.relationship('Unit', backref=db.backref('bills', lazy=True))

    @staticmethod
    def create_or_update_bill(unit_id, date_created, amount):
        existing_bill = Bill.query.filter_by(unit_id=unit_id, date_created=date_created).first()
        if existing_bill:
            existing_bill.amount = amount
            db.session.commit()
            return existing_bill, False  # False indicates that the bill was updated
        else:
            new_bill = Bill(
                unit_id=unit_id,
                date_created=date_created,
                amount=amount
            )
            db.session.add(new_bill)
            db.session.commit()
            return new_bill, True  # True indicates that a new bill was created

    def send_bill(self):
        """Mark the bill as sent and move it to the BillHistory table."""
        self.is_sent = True
        bill_history = BillHistory(
            unit_id=self.unit_id,
            amount=self.amount,
            date_sent=date.today()
        )
        db.session.add(bill_history)
        db.session.commit()

    @property
    def res_room(self):
        return self.unit.res_room if self.unit else None


class BillHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    amount = db.Column(db.Float)
    date_sent = db.Column(db.Date)
    unit = db.relationship('Unit', backref=db.backref('bill_histories', lazy=True))

    @property
    def res_room(self):
        return self.unit.res_room if self.unit else None






def update_search_vector(mapper, connection, target):
    connection.execute(
        Resident.__table__.update().
        where(Resident.id == target.id).
        values(search_vector=text('to_tsvector(\'english\', name)'))
    )


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
            current_user = Users.query.filter_by(username=data['username']).first()
            role = current_user.roles[0].name
        except:
            return make_response(jsonify({"message": "Invalid token!"}), 401)

        return f(current_user, role, *args, **kwargs)
    return decorator



db.create_all()


listen(Resident, 'after_insert', update_search_vector)
listen(Resident, 'after_update', update_search_vector)