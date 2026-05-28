from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from Exceptions.exception_handlers import register_exceptions
from routers.news_feed import news_feed
from routers.user import user
from routers.categories import section
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import httpx
import os

load_dotenv()
@asynccontextmanager
async def http_client(app:FastAPI):
    """Httpx client for making http request."""
    async with httpx.AsyncClient( timeout=httpx.Timeout(30.0)) as client:
        app.state.client = client
        mongo_client = AsyncIOMotorClient()  # Change in production
        app.state.db = mongo_client['daily_scoop']
        app.state.redis = redis.Redis(
            host='localhost',  port=6379,
            decode_responses=True
            )
        yield
        mongo_client.close()
        await app.state.redis.close()


app = FastAPI(lifespan=http_client)
app.state.default_language = 'en'
app.state.guardian_api_key = os.getenv('GuardianNewsKey')
app.state.current_api_key = os.getenv('CurrentNewsAPIKey')
app.state.free_news_key = os.getenv('FreeNewsAPIKey')
app.include_router(news_feed)
app.include_router(user)
app.include_router(section)
register_exceptions(app)

@app.get('/health')
async def health_check():
    """checks connectivity."""
    return{'OK': 'Connected'}