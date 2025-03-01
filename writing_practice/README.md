# French Writing Practice App

A Streamlit-based web application for practicing French writing and listening skills. The app generates English sentences for translation, provides text-to-speech for pronunciation practice, and offers AI-powered feedback on handwritten submissions.

## Features

- Generate practice sentences using OpenAI GPT-3.5
- Upload handwritten French translations
- Text-to-speech for pronunciation practice
- Automatic transcription using Tesseract OCR
- AI-powered grading and feedback
- Two practice modes: Writing and Listening

## Technical Stack

### Core Technologies
- Python 3.x
- Streamlit (Web Interface)
- OpenAI GPT-3.5 Turbo
- Google Text-to-Speech (gTTS)

### Dependencies
- `streamlit`: Web application framework
- `openai`: OpenAI API integration (v0.28.1)
- `python-dotenv`: Environment variable management
- `pytesseract`: OCR for handwriting recognition
- `Pillow`: Image processing
- `gTTS`: Text-to-speech functionality
- `pyyaml`: YAML file handling

## Setup

1. Install Tesseract OCR:
```bash
# On macOS
brew install tesseract tesseract-lang

# On Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fra
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Usage

### Writing Practice
1. Click "Generate New English Sentence" to get a sentence to translate
2. Write the French translation by hand
3. Take a photo or scan your writing
4. Upload the image
5. Click "Submit for Review" to get feedback

### Listening Practice
1. Click "Generate New French Audio" to get a French sentence
2. Listen to the pronunciation
3. Type what you hear
4. Click "Check Answer" to verify your transcription

## Known Issues and Solutions

### Environment Setup
- OpenAI API version compatibility (resolved by using v0.28.1)
- Proxy settings affecting API connections
- Python package conflicts with audio dependencies

### Development Issues
- Image processing reliability with different file formats
- Memory management with audio file generation
- Session state management in Streamlit

## Requirements

- Python 3.8+
- OpenAI API key
- Tesseract OCR installed
- See requirements.txt for full dependencies
