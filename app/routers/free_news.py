"""Router that contains routes for users news feed."""
from fastapi import APIRouter, Depends, Request
from app.dependencies.utilities import http_client, redis
from app.dependencies.utilities import free_news_api_categories
from app.dependencies.utilities import normalize_free_news
import os, asyncio, json
from app.errors.custom_exceptions import FreeNewsAPIError, CurrentNewsError

free_news = APIRouter(prefix='/free_news', tags=['news_feed'])

@free_news.get('/news')
async def free_news_feed(
    request:Request,
    http_client = Depends(http_client),
    redis_client = Depends(redis)
    ):
    """A route that fetches the latest news from free news api"""
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    redis_key = f'free_news_feed:{language}'   # also cache per location f'{news_category}:{lang}:{region}

    print(redis_key)  
    if redis_client:
        cached_news = await redis_client.get(redis_key)
        if cached_news:
            news = json.loads(cached_news)
            print('response from cache')
            return news
    free_news = await free_news_api_categories(http_client, language)

    result = normalize_free_news(free_news)
    if result and redis_client:
        await redis_client.set(redis_key, json.dumps(result), ex=15*60)
        print('Cached response')
    return result