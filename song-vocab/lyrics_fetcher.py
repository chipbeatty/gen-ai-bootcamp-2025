from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests
import time
import re
import json

class LyricsFetcher:
    def __init__(self):
        # Initialize the language model
        self.llm = ChatOllama(model="mistral")
        
        # Initialize DuckDuckGo
        self.ddgs = DDGS()
        self._last_request_time = 0
        self._min_delay = 5  # Minimum delay between requests
        
        # Create our tools
        self.tools = [
            Tool(
                name="search_web",
                func=self.search_web,
                description="Search for French song lyrics online. Input should be a query string."
            ),
            Tool(
                name="get_page_content",
                func=self.get_page_content,
                description="Get the content of a webpage. Input should be a URL."
            ),
            Tool(
                name="extract_lyrics",
                func=self.extract_lyrics,
                description="Extract French lyrics from webpage content. Input should be the webpage text."
            ),
            Tool(
                name="clean_lyrics",
                func=self.clean_lyrics,
                description="Clean and format lyrics text. Input should be the raw lyrics text."
            )
        ]
        
        # Create the agent prompt
        prompt = PromptTemplate.from_template(
            """You are a helpful assistant that finds French song lyrics.
            To find lyrics, follow these steps:
            1. Search for the lyrics using a French query like 'paroles [song] [artist]'
            2. From the search results, find a URL that looks like a lyrics site
            3. Get the page content from that URL
            4. Extract just the lyrics from the page content
            5. Clean up the lyrics to remove extra whitespace and annotations
            
            Use the tools provided to accomplish this task.
            If you can't find lyrics on the first try, try searching with a different query.
            
            Human: {input}
            Assistant: Let me help you find those lyrics. I'll follow the steps carefully.
            
            {agent_scratchpad}"""
        )
        
        # Create the agent
        self.agent = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def format_url(self, text: str) -> str:
        """Format text for URL (lowercase, remove accents, replace spaces)"""
        # Remove accents
        text = text.lower()
        text = text.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        text = text.replace('à', 'a').replace('â', 'a')
        text = text.replace('ô', 'o').replace('ö', 'o')
        text = text.replace('ï', 'i').replace('î', 'i')
        text = text.replace('ù', 'u').replace('û', 'u')
        text = text.replace('ç', 'c')
        
        # Replace spaces and special chars
        text = text.replace(' ', '-')
        text = re.sub(r'[^a-z0-9-]', '', text)
        return text
    
    def search_lyrics(self, artist: str, song: str) -> dict:
        """Try to find lyrics on known lyrics sites"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        for site in self.lyrics_sites:
            try:
                # Format artist and song names according to site's pattern
                formatted_artist, formatted_song = site['format'](artist, song)
                url = site['url'].format(artist=formatted_artist, song=formatted_song)
                
                print(f"Trying {site['name']}: {url}")
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = self.extract_lyrics_from_url(response.text)
                    if result['status'] == 'success':
                        return result
            except Exception as e:
                print(f"Error with {site['name']}: {str(e)}")
                continue
        
        return {"status": "error", "message": "Could not find lyrics on any known site"}
    
    def extract_lyrics_from_url(self, html_content: str) -> dict:
        """Extract lyrics from HTML content"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'meta', 'link', 'aside']):
                tag.decompose()
            
            # Look for common lyrics containers with specific site patterns
            lyrics_containers = [
                # paroles.net
                soup.find('div', class_='song-text'),
                # paroles2chansons.com
                soup.find('div', class_='content-lyrics'),
                # greatsong.net
                soup.find('div', class_='lyrics-body'),
                # genius.com
                soup.find('div', class_='lyrics'),
                # musixmatch.com
                soup.find('span', class_='lyrics__content__ok'),
                # Generic containers
                soup.find('div', class_=re.compile(r'lyrics|paroles', re.I)),
                soup.find('div', id=re.compile(r'lyrics|paroles', re.I)),
                soup.find('pre'),
                soup.find('div', class_='content')
            ]
            
            # Use the first container that has content
            lyrics = None
            for container in lyrics_containers:
                if container:
                    text = container.get_text().strip()
                    # Check if it looks like lyrics (multiple lines, not too short)
                    if text and '\n' in text and len(text) > 100:
                        lyrics = text
                        break
            
            if not lyrics:
                # If no specific container found, try to extract the largest text block
                text_blocks = []
                for p in soup.find_all(['p', 'div']):
                    text = p.get_text().strip()
                    if text and '\n' in text and len(text) > 100:
                        text_blocks.append(text)
                
                if text_blocks:
                    lyrics = max(text_blocks, key=len)
            
            if lyrics:
                # Basic cleanup
                lyrics = re.sub(r'\s*\n\s*', '\n', lyrics)  # Clean up whitespace around newlines
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Reduce multiple blank lines
                lyrics = lyrics.strip()
                
                # Remove common non-lyrics content
                lyrics = re.sub(r'(?i)paroles de la chanson.*?\n', '', lyrics)
                lyrics = re.sub(r'(?i)\[verse.*?\]|\[chorus.*?\]|\[bridge.*?\]', '', lyrics)
                lyrics = re.sub(r'(?i)verse\s*\d*:?|chorus:?|bridge:?', '', lyrics)
                
                return {
                    "status": "success",
                    "lyrics": lyrics
                }
            
            return {"status": "error", "message": "Could not extract lyrics from page"}
            
        except Exception as e:
            return {"status": "error", "message": f"Error extracting lyrics: {str(e)}"}
    
    def get_lyrics(self, artist: str, song: str) -> dict:
        """Find lyrics for a song"""
        print(f"Searching for lyrics: {song} by {artist}")
        
        # First try to find lyrics
        result = self.search_lyrics(artist, song)
        
        # If we got lyrics, clean them up
        if result["status"] == "success":
            # Basic cleanup
            lyrics = result["lyrics"]
            lyrics = re.sub(r'\s+', ' ', lyrics)  # Normalize whitespace
            lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus] etc.
            lyrics = '\n'.join(line.strip() for line in lyrics.split('\n') if line.strip())  # Clean empty lines
            
            return {
                "status": "success",
                "artist": artist,
                "song": song,
                "lyrics": lyrics
            }
        
        return result  # Return the error message
    
    def clean_lyrics(self, lyrics: str) -> str:
        """Clean and format the lyrics"""
        # Remove common artifacts and normalize spacing
        cleaned = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Verse], [Chorus] etc.
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (text in parentheses)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # Normalize line breaks
        cleaned = cleaned.strip()
        
        return cleaned

# Example usage
if __name__ == "__main__":
    fetcher = LyricsFetcher()
    result = fetcher.get_lyrics("Stromae", "Alors On Danse")
    print(result)
