"""A module that contains helper functions."""
from fastapi import Request, Depends, HTTPException
from bson import ObjectId
import os


def database(request:Request):
    """Provides database object to routes."""
    return request.app.state.db

def http_client(request:Request):
    """Provides httpx client for external network requests."""
    return request.app.state.client

def redis(request:Request):
    """Provides redis client."""
    return request.app.state.redis

async def authentication(
    request:Request, db = Depends(database), redis_client = Depends(redis)
    ):
    """identifies the user."""
    session_id = request.cookies.get('session_id')
    if not session_id:
        raise HTTPException(
            status_code = 401,
            detail = 'No session'
        )
    user_id = await redis_client.get(session_id)
    if not user_id:
        raise HTTPException(
            status_code = 401,
            detail = 'Invalid session'
        )
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code = 401,
            detail = 'Invalid user_id'
        )
    user = await db.user.find_one(
        {'_id': object_id}, 
        {'_id': 0, 'password': 0}
        )
    if not user:
        raise HTTPException(
            status_code= 404,
            detail = 'User not found'
        )
    return user
async def free_news_api_categories(
    http_client,
    lang: str | None = None,
    category: str | None = None,
    ):
    """
    A function that makes an API call to FreeNewsAPI
    to fetch news by category.
    """
    base_url = 'https://api.freenewsapi.io/v1/news'
    params = {}
    if lang is not None:
        params['language'] = lang
    
    if category is not None:
        params['topic'] = category

    try:
        print(params)
        response = await http_client.get(
            base_url, 
            params=params if params else None,
            headers={
                'x-api-key': os.getenv('FreeNewsAPIKey')
                }
            )
        return response

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=error.__class__.__name__
            )

async def current_api_categories(
    http_client,
    lang: str | None = None,
    category: str | None = None
    ):
    """
    A function that makes an API call to CurrentNews API
    to fetch news by category.
    """
    base_url = 'https://api.currentsapi.services/v1/latest-news'
    params = {
        'apiKey': os.getenv('CurrentNewsAPIKey')
    }
    if lang is not None:
        params['language'] = lang

    if category is not None:
        params['category'] = category

    try:
        response = await http_client.get(
            base_url,
            params=params if params else None
            )
        return response

    except Exception as error:
        raise HTTPException(
        status_code=500,
        detail='unable to make API call to current_news_api'
        )

def normalize(free_news_api, current_news_api):
    """
    A utility function that harmonizes the API responses of different api
    """
    news_articles = []
    for news in free_news_api['data']:
        article = {}
        article['id'] = news.get('uuid')
        article['title'] = news.get('title')
        article['url'] = news.get('url')
        article['image'] = news.get('image')
        article['published_date'] = news.get('published_at')
        article['category'] = ['politics']
        article['source'] = 'free_news'
        article['publisher'] = news.get('publisher')
        news_articles.append(article)
    for news in current_news_api['news']:
        article = {}
        article['id'] = news.get('id')
        article['title'] = news.get('title')
        article['url'] = None
        article['image'] = news.get('image')
        article['published_date'] = news.get('published')
        article['category'] = ['politics']
        article['source'] = 'current_news'
        article['publisher'] = None
        news_articles.append(article)
    return news_articles