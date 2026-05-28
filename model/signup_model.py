"""models for user data."""
from pydantic import BaseModel, EmailStr, Field

class SignUp(BaseModel):
    """Model for creating new user."""
    first_name: str
    last_name:str
    email:EmailStr
    password:str = Field(min_length=4)
    language:str