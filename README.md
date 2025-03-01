# Gen AI Bootcamp 2025

This repository contains two complementary French language learning projects:

## Projects Overview

### Writing Practice (/writing_practice)
A Streamlit application focused on:
- Handwritten French translation practice
- Text-to-speech pronunciation guides
- OCR-based handwriting recognition
- AI-powered translation feedback

### French Assistant (/french_assistant)
An advanced learning tool featuring:
- YouTube transcript-based conversation practice
- Multi-voice audio generation using AWS Polly
- Dynamic quiz generation
- RAG-based contextual responses

## Project Structure
```
gen-ai-bootcamp/
├── writing_practice/     # Writing and pronunciation practice
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
├── french_assistant/     # Conversation and listening practice
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

Please refer to each project's individual README.md for:
- Detailed feature descriptions
- Setup instructions
- Technical requirements
- Known issues and solutions

## Project Structure

```
gen-ai-bootcamp/
├── writing_practice/
│   ├── app.py           # Main application file
│   ├── requirements.txt # Project dependencies
│   └── .env            # Environment variables
└── README.md           # Project documentation
```

## Known Conflicts

### Environment Setup

- OpenAI API version compatibility (resolved by using v0.28.1)
- Proxy settings affecting API connections
- Python package conflicts with audio dependencies

### Development Issues

- Image processing reliability with different file formats
- Memory management with audio file generation
- Session state management in Streamlit

## Concerns and Future Improvements

### Security

- API key management and secure storage
- User data handling and privacy
- Input validation and sanitization

### Performance

- Audio file caching and cleanup
- API request optimization
- Image processing efficiency

### User Experience

- Error handling and user feedback
- Mobile responsiveness
- Offline functionality

### Features

- Additional language support
- Progress tracking
- User authentication
- Custom vocabulary lists

## Project Comparison with Original Template

### Architecture Differences

- **Language Focus**: Our project focuses on French, while the template targets Japanese
- **OCR Implementation**: We use pytesseract for general text recognition, while template uses MangaOCR specifically for Japanese characters
- **Framework Choice**: We settled on Streamlit after testing both frameworks, while template offers both Streamlit and Gradio implementations
- **Audio Features**: We added text-to-speech functionality for French pronunciation practice, not present in the template

### Technical Differences

- **API Version**: We use OpenAI API v0.28.1 for stability, while template uses a newer version
- **Data Source**: Our vocabulary is hardcoded/generated, while template fetches from external API endpoint
- **Error Handling**: We implemented more robust image processing error handling
- **State Management**: We use Streamlit's session state for managing application state, while template uses class-based state management

### Feature Differences

- **Practice Modes**:
  - Our Project: Writing practice and audio dictation
  - Template: Writing practice only
- **Feedback System**:
  - Our Project: Focuses on grammar and translation accuracy
  - Template: Uses JLPT N5 grammar scope and S-Rank scoring system
- **User Interface**:
  - Our Project: Tab-based navigation between practice modes
  - Template: Single-page state-based navigation

### File Structure

- **Our Project**: More streamlined with fewer files
  ```
  writing_practice/
  ├── app.py
  ├── requirements.txt
  └── .env
  ```
- **Template**: More complex structure
  ```
  writing-practice/
  ├── app.py
  ├── gradio_app.py
  ├── gradio_word.py
  ├── print.py
  ├── prompts.yaml
  ├── Tech-Specs.md
  └── requirements.txt
  ```
