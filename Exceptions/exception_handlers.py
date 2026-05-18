"""A module that handles Exceptions."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from  .custom_exceptions import FreeNewsAPIError, CurrentNewsError

def handle_free_news_error(request:Request, exception:FreeNewsAPIError):
    """Handles errors from freeNews API."""
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'error': 'True',
            'message': str(exception)
        }
    )

def handle_custom_news_error(request:Request, exception:CurrentNewsError):
    """Handles errors from custom news API."""
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'error': 'True',
            'message': str(exception)
        }
    )

def register_exceptions(app:FastAPI):
    """Registers the exception by receiving the app instance."""
    app.add_exception_handler(FreeNewsAPIError, handle_free_news_error)
    app.add_exception_handler(CurrentNewsError, handle_custom_news_error)