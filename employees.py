from app import app, db
from app.models import Employee, User
from seeder import DbSeeder

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Employee': Employee, 'User': User, 'DbSeeder': DbSeeder}
