"""A routes that handle curent news api."""
from fastapi import APIRouter, Depends, Request
from app.dependencies.utilities import http_client, redis
from app.dependencies.utilities import current_api_categories
from app.dependencies.utilities import normalize_current_news
import os, asyncio, json
from app.errors.custom_exceptions import FreeNewsAPIError, CurrentNewsError

current_news = APIRouter(prefix='/current_news', tags=['curren news api'])

@current_news.get('/latest_news')
async def latest_news(
    request:Request,
    http_client = Depends(http_client),
    redis_client = Depends(redis)
    ):
    """A route that fetches the latest news from current news api."""
    
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    redis_key = f'current_api_latest:{language}'   # also cache per location f'{news_category}:{lang}:{region}

    if redis_client:
        cached_news = await redis_client.get(redis_key)
        if cached_news:
            news = json.loads(cached_news)
            print('response from cache')
            return news
    current_news =   await current_api_categories(http_client, language)
    result = normalize_current_news(current_news)
    if current_news and redis_client:
        await redis_client.set(redis_key, json.dumps(result), ex=15*60)
        print('Cached response')
    return result


@current_news.get('/search_news')
async def latest_news(
    request:Request,
    http_client = Depends(http_client),
    search_query: str | int | float = None
    ):
    """A route that fetches the latest news from current news api."""
    
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    
    current_news =   await current_api_categories(
        http_client=http_client, lang=language, search_query=search_query
        )
    result = normalize_current_news(current_news)
    return result