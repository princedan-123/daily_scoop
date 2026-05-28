"""A module that handles Exceptions."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from  .custom_exceptions import AppError

def app_error_handler(request:Request, exception:AppError):
    """Handles errors from freeNews API."""
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'error': 'True',
            'message': str(exception)
        }
    )

def register_exceptions(app:FastAPI):
    """Registers the exception by receiving the app instance."""
    app.add_exception_handler(AppError, app_error_handler)