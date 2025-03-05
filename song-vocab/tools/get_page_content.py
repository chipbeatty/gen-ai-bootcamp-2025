import requests
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PageContent(BaseModel):
    text: str
    title: Optional[str] = None
    language: Optional[str] = None

class PageContentTool:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _extract_paroles_net(self, soup: BeautifulSoup) -> str:
        """Extract lyrics from paroles.net"""
        lyrics_div = soup.find('div', {'class': 'song-text'}) or \
                    soup.find('div', {'id': 'lyrics'}) or \
                    soup.find('div', {'class': 'content-text'}) or \
                    soup.find('div', {'class': 'text-center'}) or \
                    soup.find('div', {'class': 'lyrics-body'})
        
        if lyrics_div:
            # Remove unwanted elements
            for elem in lyrics_div.find_all(['script', 'style', 'div', 'span']):
                if any(x in (elem.get('class', []) + [elem.get('id', '')]) for x in [
                    'banner', 'ad', 'share', 'social', 'copyright', 'translation'
                ]):
                    elem.decompose()
            
            # Get text content
            text = lyrics_div.get_text('\n')
            
            # Clean up the text
            lines = [line.strip() for line in text.split('\n')]
            lines = [line for line in lines if line and not any(x in line.lower() for x in [
                'paroles', 'lyrics', 'copyright', 'translation'
            ])]
            
            return '\n'.join(lines)
        return ""

    def _extract_genius_com(self, soup: BeautifulSoup) -> str:
        """Extract lyrics from genius.com"""
        lyrics_div = soup.find('div', {'class': 'Lyrics__Container-sc-1ynbvzw-6'}) or \
                    soup.find('div', {'class': 'lyrics'}) or \
                    soup.find('div', {'data-lyrics-container': 'true'})
        
        if lyrics_div:
            return lyrics_div.get_text('\n')
        return ""

    def _extract_paroles2chansons(self, soup: BeautifulSoup) -> str:
        """Extract lyrics from paroles2chansons.com"""
        lyrics_div = soup.find('div', {'class': 'content-lyrics'}) or \
                    soup.find('div', {'class': 'song-text'})
        
        if lyrics_div:
            return lyrics_div.get_text('\n')
        return ""

    def get_content(self, url: str) -> PageContent:
        """Extract content from a webpage"""
        try:
            logger.info(f"Fetching content from: {url}")
            
            # Add more browser-like headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Check if we got a valid response
            if not response.text or len(response.text) < 100:
                logger.warning("Received empty or very short response")
                return PageContent(text="")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("Successfully parsed page content")
            
            # Try site-specific extractors first
            lyrics_text = ""
            if 'paroles.net' in url:
                lyrics_text = self._extract_paroles_net(soup)
            elif 'paroles2chansons.com' in url:
                lyrics_text = self._extract_paroles2chansons(soup)
            
            # If site-specific extraction failed, try generic approach
            if not lyrics_text:
                logger.info("Site-specific extraction failed, trying generic approach")
                # Look for common lyrics containers
                lyrics_containers = soup.find_all(['div', 'p'], class_=[
                    'lyrics', 'Lyrics', 'lyric', 'Lyric',
                    'paroles', 'Paroles', 'text-lyrics',
                    'song-text', 'SongText', 'text-center',
                    'lyrics-body', 'main-text'
                ])
                
                if lyrics_containers:
                    logger.info("Found lyrics container")
                    lyrics_text = max(lyrics_containers, key=lambda x: len(x.get_text())).get_text('\n')
            
            # Clean up lyrics
            lines = []
            for line in lyrics_text.splitlines():
                line = line.strip()
                if line and not any(x in line.lower() for x in [
                    'cookie', 'privacy', 'copyright', 'newsletter',
                    'subscribe', 'sign up', 'facebook', 'twitter',
                    'conditions', 'terms', 'contact', 'about',
                    'advertising', 'cookies', 'policy'
                ]):
                    lines.append(line)
            
            text = '\n'.join(lines)
            logger.info(f"Extracted {len(lines)} lines of text")
            
            # Basic validation
            if len(lines) < 5:
                logger.warning("Extracted text is too short to be lyrics")
                return PageContent(text="")
            
            # Get title
            title = soup.title.string if soup.title else None
            
            # Try to detect language from meta tags
            lang = soup.find('html').get('lang', None)
            
            return PageContent(
                text=text,
                title=title,
                language=lang
            )
            
        except Exception as e:
            logger.error(f"Error fetching page content: {str(e)}")
            return PageContent(text="")
