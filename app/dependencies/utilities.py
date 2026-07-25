"""A module that contains helper functions."""
from fastapi import Request, Depends, HTTPException
from bson import ObjectId
import os, httpx

def database(request:Request):
    """Provides database object to routes."""
    # return request.app.state.db

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
    lang: str,
    search_query: str | int | float = None,
    category: str | None = None,
    ):
    """
    A function that makes an API call to FreeNewsAPI
    to fetch news by category.
    """
    base_url = 'https://api.freenewsapi.io/v1/news'
    default_country = 'NG'
    param = {}
    param['language'] = lang
    if category is not None:
        param['topic'] = category
    else:
        param['country'] = default_country
    if search_query:
        param['in_title'] = search_query
    try:
        response = await http_client.get(
            base_url,
            params = param if param else None,
            headers={
                'x-api-key': os.getenv('FreeNewsAPIKey')
                }
            )
        return response
    except httpx.TimeoutException as time_error:
        print("Timeout:", repr(time_error))
        raise time_error
    except Exception as e:
        print("Other error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=e.__class__.__name__
            )

async def current_api_categories(
    http_client,
    lang: str | None = None,
    category: str | None = None,
    search_query = None
    ):
    """
    A function that makes an API call to CurrentNews API
    to fetch news by category.
    """

    latest_news_url = 'https://api.currentsapi.services/v1/latest-news'
    search_news_url = 'https://api.currentsapi.services/v1/search'
    
    params = {
        'apiKey': os.getenv('CurrentNewsAPIKey')
    }
    if search_query:
        params['keywords'] = search_query

    if lang is not None:
        params['language'] = lang

    if category is not None:
        params['category'] = category
    try:
        response = await http_client.get(
            search_news_url if search_query else latest_news_url,
            params=params if params else None
            )
        return response

    except Exception as error:
        raise HTTPException(
        status_code=500,
        detail='unable to make API call to current_news_api'
        )

def normalize_current_news(current_news_api):
    """
    A utility function that reshapes the json response of
    current news api latest endpoint api
    """
    news_articles = []
    if not isinstance(current_news_api, Exception):
        for news in current_news_api.json()['news']:
            article = {}
            article['id'] = news.get('id')
            article['title'] = news.get('title')
            article['url'] = news.get('url')
            article['image'] = news.get('image')
            article['published_date'] = news.get('published')
            article['category'] = news.get('category')
            article['source'] = 'current_news'
            article['publisher'] = None
            news_articles.append(article)
    return news_articles

def normalize_free_news(free_news_api):
    """
    A utility function that reshapes the json response
    of free news api.
    """
    news_articles = []
    if not isinstance(free_news_api, Exception):
        for news in free_news_api.json()['data']:
            article = {}
            article['id'] = news.get('uuid')
            article['title'] = news.get('title')
            article['url'] = news.get('url')
            article['image'] = news.get('image')
            article['published_date'] = news.get('published_at')
            article['category'] = news.get('category')
            article['source'] = 'free_news'
            article['publisher'] = news.get('publisher')
            news_articles.append(article)
    return news_articles