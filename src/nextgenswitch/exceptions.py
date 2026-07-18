"""Exception hierarchy for the NextGenSwitch SDK."""


class NextGenSwitchError(Exception):
    """Base SDK exception."""


class ValidationError(NextGenSwitchError, ValueError):
    """Raised when SDK input is invalid."""


class TransportError(NextGenSwitchError):
    """Raised when the API cannot be reached."""


class ApiError(NextGenSwitchError):
    """Raised for non-successful API responses."""

    def __init__(self, message: str, status_code: int, response_body: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
