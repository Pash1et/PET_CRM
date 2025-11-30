class ContactError(Exception):
    """Base exception for contact module."""

class ContactNotFound(ContactError):
    pass

class ContactAlreadyExists(ContactError):
    pass

class ContactDeleteError(ContactError):
    pass
