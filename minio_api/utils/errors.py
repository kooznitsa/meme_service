class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""
    pass


class EntityAlreadyExists(Exception):
    """Raised when a unique entity is already in database."""
    pass


class UnprocessableEntity(Exception):
    """Raised when an unprocessable entity is provided."""
    pass


class UserCredentialsError(Exception):
    """Raised when username or password are incorrect."""
    pass
