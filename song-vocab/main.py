from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn
import logging
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from tools.search_web import WebSearchTool, SearchResult
from tools.get_page_content import PageContentTool, PageContent
from tools.extract_vocabulary import VocabularyExtractor, VocabularyItem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="French Song Vocabulary Builder")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class LyricsRequest(BaseModel):
    message_request: str

class VocabularyResponse(BaseModel):
    word: str
    translation: str
    context: str

class LyricsResponse(BaseModel):
    lyrics: str
    vocabulary: List[VocabularyResponse]

class Agent:
    def __init__(self):
        self.search_tool = WebSearchTool()
        self.content_tool = PageContentTool()
        self.vocab_tool = VocabularyExtractor()
    
    def _extract_song_info(self, message: str) -> tuple[str, str]:
        # Try to extract artist and song from common formats
        patterns = [
            r'"([^"]+)"\s+by\s+"([^"]+)"',  # "Song" by "Artist"
            r'([^"]+)\s+by\s+([^"]+)',         # Song by Artist
            r'([^-]+)\s*-\s*([^-]+)'           # Song - Artist
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                song, artist = match.groups()
                return song.strip(), artist.strip()
        
        return message.strip(), ""  # Return full message as song if no pattern matches
    
    async def find_lyrics(self, message: str) -> dict:
        try:
            # Extract song and artist
            song, artist = self._extract_song_info(message)
            logger.info(f"Searching lyrics for '{song}' by '{artist}'")
            
            # Get potential URLs for lyrics sites
            results = self.search_tool.search(artist, song)
            
            if not results:
                raise ValueError("Could not generate any URLs for lyrics")
            
            lyrics = ""
            for result in results:
                logger.info(f"Trying URL: {result.url}")
                
                # Try to get content from the URL
                content = self.content_tool.get_content(result.url)
                if content and content.text:
                    potential_lyrics = content.text
                    # Basic validation of lyrics
                    lines = potential_lyrics.split('\n')
                    if len(lines) > 5 and any(len(line.strip()) > 0 for line in lines):
                        lyrics = potential_lyrics
                        logger.info(f"Found lyrics at {result.url}")
                        break
                
                # Small delay between requests
                time.sleep(2)
            
            if not lyrics:
                raise ValueError("Could not extract lyrics from any source")
            
            # Extract vocabulary
            vocab_items = self.vocab_tool.extract_vocabulary(lyrics)
            
            return {
                "lyrics": lyrics,
                "vocabulary": [
                    VocabularyResponse(
                        word=item.word,
                        translation=item.translation,
                        context=item.context
                    ) for item in vocab_items
                ]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Initialize agent
agent = Agent()

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html") as f:
        return f.read()

@app.post("/api/agent", response_model=LyricsResponse)
async def get_lyrics(request: LyricsRequest):
    return await agent.find_lyrics(request.message_request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
