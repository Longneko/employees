from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class Employee(db.Model):
    FULL_NAME_MAX_LEN = 120
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(64), nullable=False, index=True)
    position = db.Column(db.String(120), nullable=False, index=True)
    hire_date = db.Column(db.DateTime, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True,
                              default=None)
    subordinates = db.relationship('Employee', backref=db.backref('supervisor', 
                                    remote_side=[id], lazy=False))

    def __repr__(self):
        return '<{clsname} [{id}]{name}>'.format(clsname=self.__class__.__name__, id=self.id,
                                                 name=self.full_name)


class User(UserMixin, db.Model):
    USERNAME_MAX_LEN = 64
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_MAX_LEN), nullable=False, index=True, unique=True)
    email = db.Column(db.String(120), nullable=False, index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<{clsname} {name}>'.format(clsname=self.__class__.__name__, name=self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
