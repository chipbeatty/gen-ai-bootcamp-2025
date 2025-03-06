# Voice Chat Service

A voice chat service built using FastAPI, Ollama, and WebSockets. This service demonstrates the OPEA (Open Enterprise AI) architecture patterns.

## Features

- Real-time chat using WebSockets
- Integration with Ollama LLM
- Docker containerization
- Streaming responses
- Voice support (coming soon)

## Setup

1. Install Docker and Docker Compose
2. Clone this repository
3. Start the services:
```bash
# Choose your model (default is llama2:7b)
export LLM_MODEL_ID=llama2:7b

# Start the services
docker compose up
```

## Architecture

- **FastAPI Application**: Handles HTTP and WebSocket endpoints
- **Ollama Service**: Provides LLM capabilities
- **Chat Service**: Manages chat interactions
- **Audio Service**: Handles voice processing (coming soon)

## API Endpoints

- `POST /v1/chat/completions`: OpenAI-compatible chat endpoint
- `WS /ws/chat`: WebSocket endpoint for real-time chat
- `/v1/audio/transcribe`: Audio transcription (coming soon)
- `/v1/audio/synthesize`: Text-to-speech (coming soon)

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
python -m app.main
```

## Docker Support

The project includes:
- `Dockerfile`: Application container
- `docker-compose.yml`: Service orchestration
- Volume mounting for audio files
- Network configuration

## Coming Soon

- Audio transcription
- Text-to-speech
- Voice chat interface
- More LLM models
