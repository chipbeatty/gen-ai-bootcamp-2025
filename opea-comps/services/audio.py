import os
import json
import httpx
import openai
import logging
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import BinaryIO, Dict, Any, List, Optional
from .database import DatabaseService, VoicePreferenceSchema

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        self.endpoint = os.getenv("LLM_ENDPOINT", "http://localhost:8008")
        # Use local path for development
        self.audio_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "audio"
        self.audio_dir.mkdir(exist_ok=True, parents=True)
        self.db = DatabaseService()
        
        # Available voice models
        self.voice_models = {
            "en-US-Neural2-H": {"gender": "male", "age": "adult"},
            "en-US-Neural2-C": {"gender": "female", "age": "adult"},
            "en-US-Neural2-A": {"gender": "male", "age": "young"},
            "en-US-Neural2-D": {"gender": "female", "age": "young"},
            "en-GB-Neural2-B": {"gender": "male", "accent": "british"},
            "en-GB-Neural2-A": {"gender": "female", "accent": "british"},
            "en-AU-Neural2-B": {"gender": "male", "accent": "australian"},
            "en-AU-Neural2-A": {"gender": "female", "accent": "australian"}
        }
        
        # Available whisper models
        self.whisper_models = {
            "base": {"description": "Fast, good for most uses"},
            "small": {"description": "Better accuracy, still fast"},
            "medium": {"description": "Very accurate, slower"},
            "large": {"description": "Most accurate, resource intensive"}
        }
    
    async def get_available_voices(self) -> Dict[str, Dict[str, str]]:
        """Get list of available voice models"""
        return self.voice_models
    
    async def get_available_whisper_models(self) -> Dict[str, Dict[str, str]]:
        """Get list of available whisper models"""
        return self.whisper_models

    async def get_user_voice_preference(self, user_id: str) -> Dict[str, Any]:
        """Get user's voice preferences"""
        try:
            # Get preferences from database
            pref = await self.db.get_voice_preference(user_id)
            
            # VoicePreferenceSchema will always have these attributes
            return {
                "voice_id": str(pref.voice_id),
                "speaking_rate": float(pref.speaking_rate),
                "pitch": float(pref.pitch)
            }
            
        except Exception as e:
            print(f"Error getting preferences: {e}")
            # Return defaults if anything goes wrong
            return {
                "voice_id": "en-US-Neural2-H",
                "speaking_rate": 1.0,
                "pitch": 0.0
            }

    async def save_user_voice_preference(self, user_id: str, voice_id: str, speaking_rate: float = 1.0, pitch: float = 0.0) -> VoicePreferenceSchema:
        """Save user's voice preferences"""
        return await self.db.save_voice_preference(user_id, voice_id, speaking_rate, pitch)

    async def transcribe(self, audio_file: BinaryIO, model: str = "base") -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        print("\n\n=== STARTING TRANSCRIPTION ===\n\n")
        
        if model not in self.whisper_models:
            raise ValueError(f"Invalid model: {model}. Available models: {list(self.whisper_models.keys())}")
        
        # Save WebM file temporarily
        temp_path = self.audio_dir / "temp_input.webm"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save incoming audio as WebM
            print(f"Writing audio to temporary file: {temp_path}")
            with open(temp_path, "wb") as f:
                audio_data = audio_file.read()
                if not audio_data:
                    raise ValueError("Empty audio file received")
                f.write(audio_data)
                
            print(f"Saved {len(audio_data)} bytes of WebM audio")
            
            # Configure OpenAI client
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            # Create OpenAI client
            client = openai.AsyncOpenAI(api_key=openai_api_key)
            
            # Send WebM file directly to Whisper API
            print("Sending audio to Whisper API...")
            with open(temp_path, "rb") as f:
                # Call the Whisper API
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="verbose_json",
                    language="en"
                )
                
                # Debug: Print full response
                print("\nRaw Whisper API Response:")
                response_dict = response.model_dump()
                print(json.dumps(response_dict, indent=2))
                
                if not response_dict.get('text'):
                    raise ValueError("No transcription text in response")
                
                # Get segments from Whisper response
                text = response_dict['text']
                segments = response_dict.get('segments', [])
                
                logger.info("Raw response from Whisper API:")
                logger.info(json.dumps(response_dict, indent=2))
                
                logger.info("\nRaw segments from Whisper:")
                for i, seg in enumerate(segments):
                    logger.info(f"\nSegment {i}:")
                    logger.info(json.dumps(seg, indent=2))
                
                if not segments:
                    logger.warning("No segments found, creating default segment")
                    segments = [{
                        'text': text,
                        'start': 0.0,
                        'end': len(text.split()) * 0.3  # Rough estimate
                    }]
                
                # Create response with required fields
                processed_segments = [{
                    'text': seg['text'],
                    'type': 'pause' if not seg['text'].strip() else 'speech',
                    'start_time': float(seg['start']),
                    'end_time': float(seg['end'])
                } for seg in segments]
                
                logger.info("\nProcessed segments:")
                for i, seg in enumerate(processed_segments):
                    logger.info(f"\nProcessed Segment {i}:")
                    logger.info(json.dumps(seg, indent=2))
                
                response_data = {
                    'text': text,
                    'segments': processed_segments
                }
                
                logger.info("\nFinal Response:")
                logger.info(json.dumps(response_data, indent=2))
                
                return response_data
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise ValueError(f"Transcription failed: {str(e)}")
            
        finally:
            # Clean up temporary file
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {str(e)}")
    
    async def synthesize(self, text: str, user_id: str = None, voice_id: str = None, speaking_rate: float = None, pitch: float = None) -> bytes:
        """Convert text to speech with user preferences"""
        # Get user preferences if not specified
        if user_id and not all([voice_id, speaking_rate, pitch]):
            pref = await self.get_user_voice_preference(user_id)
            # Use preferences, with explicit type conversion
            voice_id = str(voice_id or pref.get('voice_id'))
            speaking_rate = float(speaking_rate if speaking_rate is not None else pref.get('speaking_rate'))
            pitch = float(pitch if pitch is not None else pref.get('pitch'))

        # Use defaults if still not set
        voice_id = str(voice_id or "en-US-Neural2-H")
        speaking_rate = float(speaking_rate or 1.0)
        pitch = float(pitch or 0.0)

        if voice_id not in self.voice_models:
            raise ValueError(f"Invalid voice_id: {voice_id}. Available voices: {list(self.voice_models.keys())}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/audio/synthesize",
                json={
                    "text": text,
                    "voice_id": voice_id,
                    "speaking_rate": speaking_rate,
                    "pitch": pitch
                }
            )
            response.raise_for_status()
            
            # Save audio temporarily and return bytes
            temp_path = self.audio_dir / "temp_output.wav"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            audio_data = sf.read(temp_path)
            temp_path.unlink()
            
            return audio_data
