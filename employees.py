from app import app, db
from sqlalchemy.inspection import inspect
from app.models import Employee, User
from app.json_encoder import CustomJSONEncoder
from app.exceptions import EmployeeError, HierarchyLoopError
from seeder import DbSeeder

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employee': Employee, 'User': User, 'DbSeeder': DbSeeder,
        'EmployeeError': EmployeeError, 'HierarchyLoopError': HierarchyLoopError,
        'CustomJSONEncoder': CustomJSONEncoder, 'inspect': inspect}
