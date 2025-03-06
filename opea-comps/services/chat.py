import os
import json
import time
import httpx
from typing import AsyncGenerator
from .models import ChatRequest, ChatResponse, Message, Role

class ChatService:
    def __init__(self):
        self.endpoint = os.getenv("LLM_ENDPOINT", "http://localhost:8008")
        self.model_id = os.getenv("LLM_MODEL_ID", "tinyllama")
        
    async def ensure_model(self) -> None:
        """Ensure the model is downloaded"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/pull",
                json={"model": self.model_id}
            )
            response.raise_for_status()
    
    async def generate(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Generate chat responses"""
        # Format messages for Ollama
        prompt = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in request.messages
        ])
        
        # Just use the last user message as the prompt
        prompt = request.messages[-1].content if request.messages else ""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": request.model,
                    "prompt": prompt,
                    "stream": request.stream,
                    "temperature": request.temperature
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            # Handle streaming response
            if request.stream:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            yield data.get("response", "")
                        except json.JSONDecodeError:
                            continue
            else:
                data = response.json()
                yield data.get("response", "")
