"""A module that contains news of different categories."""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.dependencies.utilities import http_client, current_api_categories
from app.dependencies.utilities import free_news_api_categories
from app.dependencies.utilities import normalize_free_news, redis
from app.dependencies.utilities import normalize_current_news
from app.errors.custom_exceptions import AppError, FreeNewsAPIError, CurrentNewsError
import httpx, json
import asyncio
import os, time

section = APIRouter(
    prefix='/section', 
    tags=['news sections', 'news categories']
    )

@section.get('/latest-news')
async def guardian_latest_news(
    request:Request, httpx_client = Depends(http_client)
    ):
    """Fetches latest news from guardian api."""
    guardian_api_key = request.app.state.guardian_api_key
    if not guardian_api_key:
        raise HTTPException(
            status_code=500,
            detail='Guardian API key not found'
        )
    try:
        api_url = 'https://content.guardianapis.com/search'
        response = await httpx_client.get(
            api_url, 
            params={'order-by': 'newest', 'api-key': guardian_api_key}
                )
    except httpx.ConnectTimeout as timeout:
        raise HTTPException(
            status_code=504,
            detail='http timeout occured, unable to reach server'
            )
    except Exception as request_error:
        raise HTTPException(
            status_code=500,
            detail=str(request_error)
        )
    if not response.is_success:
        raise AppError(
            'Error occured trying to access guardian api', status_code=response.status_code
            )
    latest_news = []
    for news in response.json()['response']['results']:
        article = {}
        article['id'] = news['id']
        article['title'] = news['webTitle']
        article['url'] = news['webUrl']
        article['image'] = None
        article['published_date'] = None
        article['category'] = [news['sectionName']]
        article['source'] = 'Guardian'
        article['publisher'] = 'Guardian'
        latest_news.append(article)
    return latest_news

@section.get('/free_news/{news_category}')
async def free_news_by_category(
    request:Request, news_category:str,
    http_client = Depends(http_client),
    redis = Depends(redis)
    ):
    """Routes for news by categories utilizing Free News API."""
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    redis_key = f'free_news_api_{news_category}:{language}'   # also cache per location f'{news_category}:{lang}:{region}
    if redis:
        cached_news = await redis.get(redis_key)
        if cached_news:
            news = json.loads(cached_news)
            print('from cache')
            return news
    free_news_category =  await free_news_api_categories(http_client, language, news_category)
    result = normalize_free_news(free_news_category)
    if result and redis:
        await redis.set(redis_key, json.dumps(result), ex=15*60)
        print('added to cache')
    return result

@section.get('/current_news/{news_category}')
async def current_news_by_category(
    request:Request, news_category:str,
    http_client = Depends(http_client),
    redis = Depends(redis)
    ):
    """Routes for news by categories utilizing current news API."""
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    redis_key = f'current_news_api_{news_category}:{language}'   # also cache per location f'{news_category}:{lang}:{region}
    if redis:
        cached_news = await redis.get(redis_key)
        if cached_news:
            news = json.loads(cached_news)
            print('from cache')
            return news
    current_news =  await current_api_categories(http_client, language, news_category)
    result = normalize_current_news(current_news)
    if result and redis:
        await redis.set(redis_key, json.dumps(result), ex=15*60)
        print('added to cache')
    return result