import os
import random
from datetime import date
from faker import Faker
from app import db
from app.models import Employee

fake = Faker()

class DbSeeder(object):
    DEFAULTS = {
        'positions_path': os.path.join("seeding","positions.txt"),
    }

    def __init__(self, session=None, positions=None):
        if not session:
            session = db.session
        if not positions:
            position_lvls = open(DbSeeder.DEFAULTS['positions_path'], 'r').read().split('\n')
            positions = []
            for lvl in range(len(position_lvls)):
                name, employees, salary = position_lvls[lvl].split(',')
                positions.append({
                    'name'     : name,
                    'employees': int(employees),
                    'salary': int(salary),
                })
        self.positions = positions
        self.depth_max = len(positions)
        self.session = session

    def employee_data(self, lvl):
        """Returns a dictionary with employee data (w/o subordinates or superiors) of specific
        hierarchy level. Uses random name and date.today() as hire date.
        """
        d = {
            'full_name': fake.name(),
            'position' : self.positions[lvl]['name'],
            'hire_date': date.today(),
            'salary'   : self.positions[lvl]['salary'],
        }

        return d

    def hierarchy(self, depth_max=None, lvl=0):
        """Returns an Employee object with recursively populated subordinates"""

        if depth_max is None:
            depth_max = self.depth_max

        subordinates = []
        if lvl < depth_max - 1:
            for i in range(self.positions[lvl+1]['employees']):
                subordinates.append(self.hierarchy(depth_max, lvl+1))

        return Employee(**self.employee_data(lvl), subordinates=subordinates)

    def seed(self, depth=None, auto_commit=False):
        """Adds an employee hierarchy to the db session starting from the top level.
        Commits if auto_commit is True."""
        if depth is None:
            depth = self.depth_max

        if depth > self.depth_max or depth < 1:
            raise ValueError('depth cannot be less than 1 or exceed number of position levels')

        for i in range(self.positions[0]['employees']):
            self.session.add(self.hierarchy(depth_max=depth))

        if auto_commit:
            self.session.commit()
