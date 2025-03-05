# French Song Vocabulary Builder

A tool that helps language learners build their French vocabulary through popular French songs. This project uses modern AI tools and language models to create an enriched learning experience.

## Project Overview
This application finds French song lyrics, extracts vocabulary, and provides detailed language learning insights using AI. Unlike traditional vocabulary builders, this tool focuses on French music context, cultural nuances, and modern French usage.

## Key Features (Planned)
- Search and fetch French song lyrics
- Extract vocabulary with contextual meanings
- Provide difficulty ratings for vocabulary
- Include cultural context and usage notes
- Support for various French dialects (France, Quebec, etc.)
- AI-powered example sentence generation

## Technical Concerns and Obstacles

I anticipate several challenges in developing this project:

1. **Lyric Accuracy**
   - French songs often have multiple versions and interpretations
   - Need to handle accents and special characters correctly
   - Regional variations in lyrics might exist

2. **Language Processing**
   - French word conjugations are complex
   - Need to handle contractions (l', d', etc.)
   - Identifying slang and colloquial expressions
   - Dealing with verlan (French word inversion slang)

3. **AI Integration**
   - Ensuring accurate context-aware translations
   - Balancing processing speed with accuracy
   - Managing API costs and rate limits
   - Handling model biases in language processing

4. **Data Quality**
   - Verifying the reliability of lyrics sources
   - Maintaining data freshness
   - Handling missing or incomplete data

## Unique Approaches and Enhancements

To make this project distinct, I plan to incorporate:

1. **LangChain Integration**
   - Use LangChain's agents for sophisticated web scraping
   - Implement conversation chains for interactive learning
   - Leverage memory components for user progress tracking
   - Create custom tools for French language processing

2. **Advanced AI Features**
   - Implement RAG (Retrieval Augmented Generation) for accurate cultural context
   - Use embeddings to find similar vocabulary across different songs
   - Create custom prompts for French-specific language patterns

3. **Learning Enhancements**
   - Difficulty progression system
   - Spaced repetition integration
   - Cultural context annotations
   - Pronunciation guidance using IPA

## Technical Stack
- FastAPI
- LangChain
- Ollama with Mistral 7B
- SQLite3
- Custom French language processing tools
- Vector database for semantic search

## Next Steps
1. Set up basic project structure
2. Implement core lyric fetching functionality
3. Develop French-specific vocabulary extraction
4. Add LangChain agents and tools
5. Create cultural context enhancement features

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
