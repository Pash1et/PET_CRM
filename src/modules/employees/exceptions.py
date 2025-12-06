class EmployeeError(Exception):
    """Base exception for employee module."""


class EmployeeNotFound(EmployeeError):
    pass

class EmployeeDeleteError(EmployeeError):
    pass

class EmployeeAlreadyExists(EmployeeError):
    pass

class LoginError(EmployeeError):
    pass
