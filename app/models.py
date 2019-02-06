from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates
from sqlalchemy.inspection import inspect
from app import db, login, exceptions

class ModelJSONifiable():
    """A mixin class that provides basic funcitonal to produce JSON encoding compliant dictionaries
    by omitting Model relationship attributes to avoid circular references or loading 
    unnecessary objects.
    """
    def relationships(self):
        cls = self.__class__
        return [str(rel)[len(cls.__name__)+1:] for rel in inspect(cls).relationships]

    def toJSONifiable(self, no_relationships=True):
        """Returns a DB Model child object as dictionary. Excludes relationship attributes if
        no_relationships == True (to avoid circular references)."""
        relationships = [] if no_relationships else self.relationships()
        d = {key: val for key, val in self.__dict__.items() if not key.startswith('_')
            and not key in relationships}
        return d


class Employee(ModelJSONifiable, db.Model):
    FULL_NAME_MAX_LEN = 120
    POSITION_NAME_MAX_LEN = 120
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(FULL_NAME_MAX_LEN), nullable=False, index=True)
    position = db.Column(db.String(POSITION_NAME_MAX_LEN), nullable=False, index=True)
    hire_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True,
                              default=None)
    subordinates = db.relationship('Employee', backref=db.backref('supervisor', 
                                    remote_side=[id], lazy=True))

    def transfer_subs(self, replacement):
        """Transfer all subordinates to another supervisor. Commits to db if auto_commit == True"""
        # Uses reversed list because changing the supervisor immediately removes sub from the
        # subordinates list
        for sub in reversed(self.subordinates):
            sub.supervisor = replacement
            
    def _get_all_subordinates(self):
        for s in self.subordinates:
            yield s
            yield from s._get_all_subordinates()

    @validates('supervisor')
    def validate_supervisor(self, key, supervisor):
        for sub in self._get_all_subordinates():
            if sub == supervisor:
                raise exceptions.HierarchyLoopError(self, supervisor)
        return supervisor

    def toJSONifiable(self, no_relationships=True):
        """Extends the corresponding ModelJSONifiable method by adding following fields:
          subordinates_id: list of the ids of the subordiantes
          supervisor: string representation of supervisor
        """
        d = super().toJSONifiable(no_relationships=True)
        d['subordinates_id'] = [s.id for s in self.subordinates]
        d['supervisor'] = str(self.supervisor)
        return d

    def __repr__(self):
        return '<{clsname} [{id}]{name}>'.format(clsname=self.__class__.__name__, id=self.id,
                                                 name=self.full_name)

    def __str__(self):
        return '[{id}] {name}'.format(id=self.id, name=self.full_name)


class User(UserMixin, db.Model):
    USERNAME_MAX_LEN = 64
    EMAIL_MAX_LEN = 64
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USERNAME_MAX_LEN), nullable=False, index=True, unique=True)
    email = db.Column(db.String(EMAIL_MAX_LEN), nullable=False, index=True, unique=True)
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
