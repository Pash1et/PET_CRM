from exceptions import BaseProjectException


class WazzupError(Exception):
    """Base exception for the Wazzup module."""


class WazzupTransportError(WazzupError):
    pass


class WazzupApiError(WazzupError):
    def __init__(self, status_code: int, message: str | None = None):
        self.status_code = status_code
        super().__init__(message or f"Wazzup API error {status_code}")


class WazzupUnavailable(BaseProjectException):
    status_code = 502
    detail = "Wazzup service unavailable"
