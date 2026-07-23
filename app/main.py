from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.errors.exception_handlers import register_exceptions
from app.routers.current_news import current_news
from app.routers.user import user
from app.routers.free_news import free_news
from app.routers.free_news_detail import free_news_article
from app.routers.categories import section
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import httpx
import os

origins = [
    "daily-scoop-frontend.vercel.app",
    "https://daily-scoop-frontend.vercel.app/",
    "https://daily-scoop-frontend.vercel.app",
    "http://127.0.0.1:5173",
    "http://localhost:5173"
]
load_dotenv()
@asynccontextmanager
async def http_client(app:FastAPI):
    """Httpx client for making http request."""
    async with httpx.AsyncClient( timeout=httpx.Timeout(60.0)) as client:
        app.state.client = client
        # mongo_client = AsyncIOMotorClient()  # Change in production
        # app.state.db = mongo_client['daily_scoop']
        app.state.redis = redis.Redis.from_url(
            os.getenv('REDIS_URL'),
            decode_responses=True
            )
        yield
        # mongo_client.close()
        await app.state.redis.close()


app = FastAPI(lifespan=http_client)
app.state.default_language = 'en'
app.state.guardian_api_key = os.getenv('GuardianNewsKey')
app.state.current_api_key = os.getenv('CurrentNewsAPIKey')
app.state.free_news_key = os.getenv('FreeNewsAPIKey')
app.include_router(current_news)
app.include_router(user)
app.include_router(free_news)
app.include_router(section)
app.include_router(free_news_article)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,          
    allow_methods=["*"],             
    allow_headers=["*"],
    )
register_exceptions(app)

@app.get('/health')
async def health_check():
    """checks connectivity."""
    return{'OK': 'Connected'}