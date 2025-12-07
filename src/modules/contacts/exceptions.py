from exceptions import BaseProjectException


class ContactError(BaseProjectException):
    """Base exception for contact module."""

class ContactNotFound(ContactError):
    status_code = 404
    detail = "Contact not found"

class ContactAlreadyExists(ContactError):
    status_code = 409
    detail = "Contact already exists"

class ContactDeleteError(ContactError):
    status_code = 400
    detail = "Contact cannot be deleted"
