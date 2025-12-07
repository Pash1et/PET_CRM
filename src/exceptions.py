class BaseProjectException(Exception):
    """
    The base class for all custom exceptions of the application.
    """
    status_code: int
    detail: str

    def __init__(self, detail: str = None):
        self.detail = detail or self.detail
        super().__init__(self.detail)
