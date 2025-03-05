import re
from typing import List, Dict
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str

class WebSearchTool:
    def __init__(self):
        self.lyrics_sites = [
            {
                'name': 'paroles.net',
                'url_pattern': 'https://www.paroles.net/{artist}/paroles-{song}',
                'artist_transform': lambda x: x.lower().replace(' ', '-') if x else 'indila',
                'song_transform': lambda x: x.lower().replace(' ', '-')
            }
        ]
        
    def _reset_backoff(self):
        """Reset the backoff delay to minimum"""
        self._current_delay = self._min_delay
        
    def _increase_backoff(self):
        """Increase the backoff delay"""
        self._current_delay *= self._backoff_factor

    def _clean_text(self, text: str) -> str:
        """Clean text for URL construction"""
        # Convert accented characters to non-accented
        text = text.replace('é', 'e').replace('è', 'e').replace('ê', 'e')\
                   .replace('à', 'a').replace('â', 'a')\
                   .replace('î', 'i').replace('ï', 'i')\
                   .replace('ô', 'o').replace('ö', 'o')\
                   .replace('û', 'u').replace('ù', 'u')\
                   .replace('ç', 'c')
        
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def search(self, artist: str, song: str, max_results: int = 2) -> List[SearchResult]:
        """Generate potential lyrics URLs"""
        try:
            results = []
            
            # Clean artist and song names
            artist = self._clean_text(artist)
            song = self._clean_text(song)
            
            for site in self.lyrics_sites:
                try:
                    # Transform artist and song names according to site's format
                    artist_fmt = site['artist_transform'](artist)
                    song_fmt = site['song_transform'](song)
                    
                    # Generate URL
                    url = site['url_pattern'].format(
                        artist=artist_fmt,
                        song=song_fmt
                    )
                    
                    logger.info(f"Generated URL for {site['name']}: {url}")
                    
                    results.append(SearchResult(
                        url=url,
                        title=f"Lyrics for {song} by {artist} on {site['name']}",
                        snippet=""
                    ))
                    
                    if len(results) >= max_results:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error generating URL for {site['name']}: {str(e)}")
                    continue
            
            return results
                
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
