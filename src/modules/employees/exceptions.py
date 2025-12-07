from exceptions import BaseProjectException


class EmployeeError(BaseProjectException):
    """Base exception for employee module."""


class EmployeeNotFound(EmployeeError):
    status_code = 404
    detail = "Employee not found"


class EmployeeDeleteError(EmployeeError):
    status_code = 400
    detail = "Employee cannot be deleted"


class EmployeeAlreadyExists(EmployeeError):
    status_code = 409
    detail = "Employee already exists"


class EmployeeLoginError(EmployeeError):
    status_code = 401
    detail = "Invalid credentials or account inactive"

class EmployeeForbidden(EmployeeError):
    status_code = 403
    detail = "You are not authorized to perform this action"
