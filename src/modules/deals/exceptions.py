class DealError(Exception):
    """Base exception for deals module."""


class DealNotFound(DealError):
    pass


class DealDeleteError(DealError):
    pass
