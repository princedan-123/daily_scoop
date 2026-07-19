"""Router that contains routes for users news feed."""
from fastapi import APIRouter, Depends, Request
from app.dependencies.utilities import http_client, redis
from app.dependencies.utilities import free_news_api_categories
from app.dependencies.utilities import current_api_categories
from app.dependencies.utilities import normalize
import os, asyncio, json
from app.errors.custom_exceptions import FreeNewsAPIError, CurrentNewsError

news_feed = APIRouter(tags=['news_feed'])

@news_feed.get('/news_feed')
async def feed(
    request:Request,
    http_client = Depends(http_client),
    redis_client = Depends(redis)
    ):
    """News feed."""
    language = request.cookies.get('lang_pref')
    if not language:
        language = request.app.state.default_language
    redis_key = f'{news_feed}:{language}'   # also cache per location f'{news_category}:{lang}:{region}
   
    if redis_client:
        cached_news = await redis_client.get(redis_key)
        if cached_news:
            news = json.loads(cached_news)
            print('response from cache')
            return news
    free_news, current_news = await asyncio.gather(
        free_news_api_categories(http_client, language),
        current_api_categories(http_client, language),
        return_exceptions=True
        )
    result = normalize(free_news, current_news)
    if result and redis_client:
        await redis_client.set(redis_key, json.dumps(result), ex=15*60)
        print('Cached response')
    return result