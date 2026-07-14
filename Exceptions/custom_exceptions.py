"""A module that contains custom exceptions for error handling."""

class AppError(Exception):
    """Base Exception for all Errors."""
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.name= self.__class__.__name__
        self.status_code=status_code

class FreeNewsAPIError(AppError):
    """
    An Exception to be raised if an error occurs
    while using FreeNewsAPI
    """
    pass

class CurrentNewsError(AppError):
    """
    An Exception to be raised if an error occurs
    while using CurrentNews API.
    """
    pass

class SignUpError(AppError):
    """
    An Exception to be raised if an error
    while creating a new user
    """
    pass 