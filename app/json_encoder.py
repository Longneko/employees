from datetime import date, datetime
from flask.json import JSONEncoder
from sqlalchemy.inspection import inspect
from app.models import Employee

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            d = {
                Employee: lambda : self.employee(obj),
                date    : lambda : self.date(obj),
                datetime: lambda : self.datetime(obj),
            }
            return d[obj.__class__]()

            iterable = iter(obj)
        except (KeyError, TypeError):
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

    def date(self, date, format='%Y-%m-%d'):
        return date.strftime(format)

    def datetime(self, datetime, format='%Y-%m-%dT%H:%M:%S'):
        return datetime.strftime(format)

    def model_to_dict(self, obj, no_relationships=True):
        """Returns a DB Model child object as dictionary. Excludes relationship attributes if
        no_relationships == True (to avoid circular references)."""
        if no_relationships:
            cls = obj.__class__
            relationships = [str(rel)[len(cls.__name__)+1:] for rel in inspect(cls).relationships]
        else:
            relationships = []
        d = {key: val for key, val in obj.__dict__.items() if not key.startswith('_')
            and not key in relationships}
        return d

    def employee(self, employee):
        """Returns an Employee object as dicitonary without relationship attributes (to avoid
        circular references) and loading entire hierarchy with each employee. Adds following fields:
          subordinates_id: list of the ids of the subordiantes
          supervisor: string representation of supervisor
        """
        d = self.model_to_dict(employee, no_relationships=True)
        d['subordinates_id'] = [s.id for s in employee.subordinates]
        d['supervisor'] = str(employee.supervisor)
        return d
