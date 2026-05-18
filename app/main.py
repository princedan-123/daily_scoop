from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from Exceptions.exception_handlers import register_exceptions
from routers.news_feed import news_feed
import httpx

load_dotenv()
@asynccontextmanager
async def http_client(app:FastAPI):
    """Httpx client for making http request."""
    async with httpx.AsyncClient() as client:
        app.state.client = client
        yield

app = FastAPI(lifespan=http_client)
app.include_router(news_feed)
register_exceptions(app)

@app.get('/health')
async def health_check():
    """checks connectivity."""
    return{'OK': 'Connected'}