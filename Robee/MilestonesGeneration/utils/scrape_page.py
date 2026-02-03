# scrape_page.py
import asyncio
import os
from dotenv import load_dotenv
from firecrawl import AsyncFirecrawlApp
from firecrawl import ScrapeOptions

# Load environment variables from .env file
load_dotenv()

async def main(web_url):
    app = AsyncFirecrawlApp(api_key=os.getenv('Firecrawlapi'))
    
    try:
        response = await app.scrape_url(
            url=web_url,		
            formats= [ 'markdown' ],
            only_main_content= True , 
            parse_pdf= True,
        )
        
        if hasattr(response, 'markdown'):
            content = response.markdown
        elif hasattr(response, 'data') and isinstance(response.data, dict):
            content = response.data.get('markdown', str(response.data))
        elif hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        return content
    except Exception as e:
        print(f"Error occurred: {e}")
        return None