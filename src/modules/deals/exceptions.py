from exceptions import BaseProjectException


class DealError(BaseProjectException):
    """Base exception for deals module."""


class DealNotFound(DealError):
    status_code = 404
    detail = "Deal not found"


class DealDeleteError(DealError):
    status_code = 400
    detail = "Deal cannot be deleted"
