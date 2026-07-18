from fastapi import APIRouter, Depends, Request
from app.dependencies.utilities import http_client, redis
from app.dependencies.utilities import normalize, redis
import os, json

free_news_article = APIRouter(tags=['free_news_article_details'])

@free_news_article.get('/free_news_article/{article_id}')
async def news_details(
    article_id:str, http_client = Depends(http_client),
    # redis_client = Depends(redis)
    ):
    """
    A route that fetches an article news detail from
    free news api.
    """
    #  check cache
    # redis_key = article_id
    if redis_client:
        cached_news = await redis_client.get(redis_key)
        if cached_news:
            deserialized_data = json.loads(cached_news)
            return deserialized_data
    try:
        response = await http_client.get(
            'https://api.freenewsapi.io/v1/details',
            params={'uuid' : article_id},
            headers={
                'x-api-key': os.getenv('FreeNewsAPIKey')
                }
                )
        response = response.json()
        # if response and redis_client:
        #     await redis_client.set(redis_key, json.dumps(response), ex=60*60)
        return response

    except httpx.TimeoutException as time_error:
        print("Timeout:", repr(time_error))
        raise time_error
    except Exception as e:
        print("Other error:", repr(e))
        raise HTTPException(
            status_code=500,
            detail=error.__class__.__name__
            )

