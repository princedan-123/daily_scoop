"""Module for user routes."""
from fastapi import APIRouter, Response, Request, Depends
from model.signup_model import SignUp
from Exceptions.custom_exceptions import SignUpError
from uuid import uuid4
from dependencies.utilities import database, redis, authentication
import bcrypt

user = APIRouter(prefix='/user', tags=['user_routes'])

@user.post('/create')
async def signup(
    request:Request, signup_data:SignUp, response:Response,
    db = Depends(database),
    redis = Depends(redis)
    ):
    """A route that creates new users."""
    #  check if user already exists
    existing_user = await db.user.find_one({'email': signup_data.email})
    if existing_user:
        raise SignUpError('user already exists', status_code=409)
    #  hash the password
    hashed_pw = bcrypt.hashpw(
        signup_data.password.encode(), bcrypt.gensalt()
        )
    user_data = signup_data.model_dump()
    user_data['password'] = hashed_pw.decode()
    result = await db.user.insert_one(user_data)
    if result.inserted_id:
        session_id = str(uuid4())
        user_id = result.inserted_id
        await redis.set(session_id, str(user_id), ex=60*60)
        response.set_cookie(
            key='session_id', value=session_id,  # change cookies in production for security
            httponly=True, secure=False,
            samesite='lax', max_age= 60*60
        )
        response.set_cookie(
            key='lang_pref', value=user_data['language'],
            httponly=True, secure=False,  #  change settings in production
            samesite='lax', max_age=60*60
        )
        return {
            'status': 'ok',
            'message': f'welcome {signup_data.last_name}'
            }
    raise SignUpError('could not create user')

@user.get('/login')
async def login(user = Depends(authentication)):
    """A routes that logins in users."""
    print(user)
    if user:
        return {
            'status': 'ok',
            'message': 'logged in'
        }



