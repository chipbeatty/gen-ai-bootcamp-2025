# French Song Vocabulary Builder

A tool that helps language learners build their French vocabulary through popular French songs. I've built this as part of the Codeium GenAI Bootcamp, with some key differences from the original project design.

## Project Overview

This application finds French song lyrics and extracts useful vocabulary with translations and context. It uses direct web scraping of lyrics sites combined with local AI for vocabulary analysis.

## Key Features

- Search and fetch French song lyrics from paroles.net
- Extract vocabulary with translations and contextual examples
- Clean, readable UI optimized for desktop viewing
- Local AI processing using Ollama/Mistral for vocabulary analysis

## Screenshots

### 1. Main Interface

![Song Vocab](song-vocab/docs/screenshots/song_vocab_builder.png)

## Implementation Details

### Key Differences from Original Design

1. **Lyrics Fetching**

   - Switched from SerpAPI to direct web scraping
   - Focused on paroles.net as primary source after testing multiple sites
   - Implemented robust HTML parsing with BeautifulSoup

2. **AI Integration**

   - Using local Ollama/Mistral instead of OpenAI
   - Custom prompt engineering for vocabulary extraction
   - No RAG or embeddings - keeping it simple and effective

3. **User Interface**
   - Optimized for readability with wide layout
   - No scrolling sections - full content display
   - Three-line vocabulary format for clear presentation

### Agent Implementation

I used a LangChain agent with Ollama/Mistral to coordinate the lyrics fetching process. The agent orchestrates several custom tools:

1. **Search Web Tool**

   - Searches for French lyrics using formatted queries
   - Handles URL patterns for different lyrics sites
   - Returns potential lyrics page URLs

2. **Get Page Content Tool**

   - Fetches webpage content with proper headers
   - Handles rate limiting and retries
   - Manages character encoding for French text

3. **Extract Lyrics Tool**

   - Uses BeautifulSoup to parse HTML
   - Identifies lyrics containers using site-specific patterns
   - Cleans up annotations and formatting

4. **Clean Lyrics Tool**
   - Removes unwanted sections ([Verse], [Chorus], etc.)
   - Normalizes whitespace and line breaks
   - Preserves French accents and special characters

### RAG System

I implemented a simple but effective RAG approach for vocabulary extraction:

1. **Retrieval**

   - Extract full context lines from lyrics
   - Maintain line breaks and formatting
   - Preserve song structure for context

2. **Augmentation**

   - Custom prompt engineering for vocabulary identification
   - French language expertise built into prompts
   - Example-based formatting for consistent output

3. **Generation**
   - Structured vocabulary output with translations
   - Context-aware word selection
   - Focus on learner-appropriate vocabulary

### Technical Challenges Solved

1. **Rate Limiting**

   - Initially hit 403/404 errors with lyrics sites
   - Added proper user agent headers
   - Implemented URL pattern matching for different sites

2. **Content Extraction**

   - Developed specific HTML parsing for lyrics containers
   - Added cleanup for annotations and extra whitespace
   - Fixed character encoding for French accents

3. **AI Response Formatting**
   - Structured prompt to ensure consistent vocabulary format
   - Added streaming response handling for Ollama
   - Improved error handling for AI responses

## Technical Stack

- FastAPI for backend API
- Ollama with Mistral 7B for local AI
- BeautifulSoup4 for HTML parsing
- Tailwind CSS for styling
- Custom tools for lyrics fetching and vocabulary extraction

## Setup and Usage

1. Install dependencies: `pip install -r requirements.txt`
2. Make sure Ollama is running with Mistral model
3. Run the app: `python main.py`
4. Open browser and search for your favorite French songs
