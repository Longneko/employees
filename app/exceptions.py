class EmployeeError(Exception):
    """Basic exception for errors raised by Employee class"""
    def __init__(self, employee, msg=None):
        if msg is None:
            msg = 'An error occured employee {}'.format(employee)
        super().__init__(msg)
        self.employee = employee

class HierarchyLoopError(EmployeeError):
    """Raised when employee has their any level subordinate set as supervisor creating a loop"""
    def __init__(self, employee, supervisor):
        if employee == supervisor:
            msg = 'Cannot set self ({}) as supervisor)'.format(employee)
        else:
            msg = 'Cannot set subordinate ({}) as supervisor for ({})'.format(supervisor, employee)
        super().__init__(employee, msg)
        self.supervisor = supervisor
