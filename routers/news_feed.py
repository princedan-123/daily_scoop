"""Router that contains routes for users news feed."""
from fastapi import APIRouter, Request
import os, asyncio
from Exceptions.custom_exceptions import FreeNewsAPIError, CurrentNewsError

news_feed = APIRouter(prefix="/news_feed", tags=['news_feed'])
free_news_base_url='https://api.freenewsapi.io/v1'
current_news_base_url='https://api.currentsapi.services/v1/latest-news'

@news_feed.get('/anonymous')
async def anonymous_feed(request:Request ):
    """News feed for anonymous users."""

    feed:[dict] = []
    async def fetch_from_free_news():
        """Fetches news from free news API."""
        free_news = await request.app.state.client.get(
            f'{free_news_base_url}/news', headers={'x-api-key':os.getenv('FreeNewsAPIKey')}
            )
        return free_news

    async def fetch_from_current_news():
        """Fetches news from current news API."""
        current_news = await request.app.state.client.get(
            f"{current_news_base_url}?apiKey={os.getenv('CurrentNewsAPIKey')}"
            )
        return current_news
    
    free_news, current_news = await asyncio.gather(
        fetch_from_free_news(), 
        fetch_from_current_news(), 
        return_exceptions=True
        )
    print(current_news)  
    if isinstance(free_news, Exception):
        raise FreeNewsAPIError('failed to access free news API')
    if isinstance(current_news, Exception):
        raise CurrentNewsError('failed to access current news API')
    if not current_news.is_success:
        raise CurrentNewsError(
            'server Error from Current news API',
            status_code = current_news.status_code
            )
    if not free_news.is_success:
        raise FreeNewsAPIError(
            'server Error from Free news API',
            status_code=free_news.status_code
            )
    current_news_data = current_news.json()
    for news in current_news_data['news']:
        article = {}
        article['news_article'] = news.get('id')
        article['title'] = news.get('title')
        article['url'] = news.get('url')
        article['image'] = news.get('image')
        article['published_date'] = news.get('published')
        article['category'] = news.get('category', [None])
        article['author'] = news.get('author')
        article['source'] = 'CurrentNews'
        article['publisher'] = None
        feed.append(article)
            
    
    free_news_data = free_news.json()
    for news in free_news_data['data']:
        article = {}
        article['news_article'] = news.get('uuid')
        article['title'] = news.get('title')
        article['url'] = None
        article['image'] = None
        article['published_date'] = news.get('published_at')
        article['category'] = None
        article['author'] = None
        article['source'] = 'FreeNews'
        article['publisher'] = news.get('publisher')
        feed.append(article)
    return feed
    
