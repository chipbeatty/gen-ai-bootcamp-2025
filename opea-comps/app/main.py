import sys
import logging
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from services.models import ChatRequest, ChatResponse, AudioRequest, AudioResponse
from services.chat import ChatService
from services.audio import AudioService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from services.database import (
    DatabaseService, get_session, ConversationSchema, VoicePreferenceSchema
)
from sqlalchemy.orm import Session
import json
import io
import time
from typing import List, Optional

app = FastAPI(title="Voice Chat Service")
chat_service = ChatService()
audio_service = AudioService()
db_service = DatabaseService()

@app.get("/test")
def test():
    print("Test endpoint called!")
    sys.stdout.write("\n=== TEST ENDPOINT CALLED ===\n")
    sys.stdout.flush()
    return {"message": "Test successful!"}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/api/voices")
async def get_voices():
    """Get available voice models"""
    return await audio_service.get_available_voices()

@app.get("/api/whisper-models")
async def get_whisper_models():
    """Get available whisper models"""
    return await audio_service.get_available_whisper_models()

@app.get("/api/voice-preference/{user_id}")
async def get_voice_preference(user_id: str):
    """Get user's voice preferences"""
    try:
        prefs = await audio_service.get_user_voice_preference(user_id)
        if not prefs or not isinstance(prefs, dict):
            return {
                "voice_id": "en-US-Neural2-H",
                "speaking_rate": 1.0,
                "pitch": 0.0
            }
        return {
            "voice_id": str(prefs.get("voice_id", "en-US-Neural2-H")),
            "speaking_rate": float(prefs.get("speaking_rate", 1.0)),
            "pitch": float(prefs.get("pitch", 0.0))
        }
    except Exception as e:
        print(f"Error getting voice preferences: {e}")
        return {
            "voice_id": "en-US-Neural2-H",
            "speaking_rate": 1.0,
            "pitch": 0.0
        }

@app.post("/api/voice-preference/{user_id}")
async def save_voice_preference(user_id: str, voice_id: str, speaking_rate: float = 1.0, pitch: float = 0.0):
    """Save user's voice preferences"""
    return await audio_service.save_user_voice_preference(user_id, voice_id, speaking_rate, pitch)

@app.get("/api/conversations/{user_id}")
async def get_conversations(user_id: str, session: Session = Depends(get_session)) -> List[ConversationSchema]:
    """Get user's conversation history"""
    return await db_service.get_conversations(user_id)

@app.post("/api/conversations/{user_id}")
async def save_conversation(
    user_id: str,
    conversation: dict,
    session: Session = Depends(get_session)
):
    """Save a conversation"""
    title = conversation.get('title', '')
    messages = {
        str(i): msg for i, msg in enumerate(conversation.get('messages', []))
    }
    model_settings = conversation.get('model_settings', {})
    return await db_service.save_conversation(user_id, title, messages, model_settings)

@app.on_event("startup")
async def startup_event():
    """Ensure model is downloaded on startup"""
    await chat_service.ensure_model()

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Handle chat completions"""
    if request.stream:
        return StreamingResponse(
            chat_service.generate(request),
            media_type="text/event-stream"
        )
    
    # For non-streaming, collect the full response
    response = ""
    async for chunk in chat_service.generate(request):
        response += chunk
    
    return ChatResponse(
        id=f"chat-{int(time.time())}",
        model=request.model,
        created=int(time.time()),
        choices=[{
            "message": {
                "role": "assistant",
                "content": response
            },
            "finish_reason": "stop"
        }],
        usage={
            "prompt_tokens": len(request.messages[-1].content.split()),
            "completion_tokens": len(response.split()),
            "total_tokens": len(request.messages[-1].content.split()) + len(response.split())
        }
    )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time chat"""
    sys.stdout.write("\n\n=== CHAT WEBSOCKET CONNECTED ===\n\n")
    sys.stdout.flush()
    
    await websocket.accept()
    sys.stdout.write("WebSocket accepted\n")
    sys.stdout.flush()
    
    try:
        while True:
            # Receive and parse the request
            data = await websocket.receive_text()
            request = ChatRequest.model_validate_json(data)
            
            # Generate and stream the response
            async for chunk in chat_service.generate(request):
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": chunk
                }))
            
            # Send end marker
            await websocket.send_text(json.dumps({
                "type": "end"
            }))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": str(e)
        }))
    finally:
        await websocket.close()

@app.post("/api/audio/transcribe")
async def transcribe_audio(file: UploadFile = File(...), model: str = "base"):
    """Transcribe audio file to text"""
    sys.stdout.write("\n\n=== ENDPOINT CALLED ===\n\n")
    sys.stdout.flush()
    print("Content type:", file.content_type)
    sys.stdout.flush()
    try:
        # Log detailed request info
        sys.stdout.write("\n=== Transcription Request Details ===\n")
        sys.stdout.write(f"File name: {file.filename}\n")
        sys.stdout.write(f"Content type: {file.content_type}\n")
        sys.stdout.write(f"File size: {len(await file.read())} bytes\n")
        await file.seek(0)  # Reset file position after reading
        
        # Log headers
        sys.stdout.write("\nRequest headers:\n")
        for name, value in file.headers.items():
            sys.stdout.write(f"{name}: {value}\n")
        sys.stdout.flush()
        
        # Validate content type
        content_type = file.content_type or ''
        if not content_type.startswith(('audio/', 'video/webm')):
            error_msg = f"Invalid content type: {content_type}. Must be audio/* or video/webm"
            sys.stdout.write(f"\nError: {error_msg}\n")
            sys.stdout.write("Supported types: audio/*, video/webm\n")
            sys.stdout.flush()
            raise ValueError(error_msg)
        
        # Read file into memory
        logger.info(f"Processing audio file: {file.filename} ({content_type})")        
        contents = await file.read()
        if not contents:
            raise ValueError("Empty audio file received")
            
        logger.info(f"Read {len(contents)} bytes of audio data")
        audio_file = io.BytesIO(contents)
        audio_file.name = file.filename
        
        # Transcribe
        try:
            result = await audio_service.transcribe(audio_file, model)
            logger.info("Got transcription result:")
            logger.info(json.dumps(result, indent=2))
            
            # Validate response has required fields
            if not isinstance(result, dict):
                raise ValueError(f"Invalid response type: {type(result)}")
            if 'text' not in result:
                raise ValueError("Response missing 'text' field")
            if 'segments' not in result:
                raise ValueError("Response missing 'segments' field")
                
            # Create response model
            response = AudioResponse(**result)
            logger.info("Created AudioResponse:")
            logger.info(response.model_dump_json(indent=2))
            return response
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise ValueError(f"Failed to transcribe audio: {str(e)}")
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e) or "Invalid request"
        )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e) or "Internal server error"
        )

@app.post("/api/audio/synthesize")
async def synthesize_speech(
    text: str,
    user_id: Optional[str] = None,
    voice_id: Optional[str] = None,
    speaking_rate: Optional[float] = None,
    pitch: Optional[float] = None
):
    """Convert text to speech with user preferences"""
    try:
        audio_data = await audio_service.synthesize(
            text,
            user_id=user_id,
            voice_id=voice_id,
            speaking_rate=speaking_rate,
            pitch=pitch
        )
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
