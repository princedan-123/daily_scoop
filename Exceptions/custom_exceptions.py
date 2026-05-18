"""A module that contains custom exceptions for error handling."""

class FreeNewsAPIError(Exception):
    """
    An Exception to be raised if an error occurs
    while using FreeNewsAPI
    """
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code=status_code

class CurrentNewsError(Exception):
    """
    An Exception to be raised if an error occurs
    while using CurrentNews API.
    """
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.status_code=status_code
    