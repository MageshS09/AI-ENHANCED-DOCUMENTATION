"""Application-specific exceptions."""


class AppError(Exception):
    """Base class for expected application errors."""

    status_code = 400
    public_message = "Request could not be completed."

    def __init__(self, message: str | None = None) -> None:
        """Create an application error with a public message."""
        super().__init__(message or self.public_message)
        self.public_message = message or self.public_message


class RepositoryCloneError(AppError):
    """Raised when a repository cannot be cloned."""

    status_code = 422
    public_message = "Unable to clone the repository. Confirm it is public and the URL is correct."


class ConfigurationError(AppError):
    """Raised when required server configuration is missing."""

    status_code = 500
    public_message = "Server configuration is incomplete."
