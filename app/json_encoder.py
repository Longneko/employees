from datetime import date, datetime
from flask.json import JSONEncoder
from sqlalchemy.inspection import inspect
from app.models import Employee

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return obj.toJSONifiable()
        except AttributeError:
            pass

        try:
            d = {
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
