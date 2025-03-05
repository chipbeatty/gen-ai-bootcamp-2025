import requests
import json
from typing import List, Dict
from pydantic import BaseModel
import re

class VocabularyItem(BaseModel):
    word: str
    translation: str
    context: str

class VocabularyExtractor:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "mistral"

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API and accumulate streaming response"""
        response = requests.post(
            self.ollama_url,
            json={"model": self.model, "prompt": prompt},
            stream=True
        )
        
        # Accumulate the streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    full_response += json_response['response']
        
        return full_response

    def extract_vocabulary(self, lyrics: str) -> List[VocabularyItem]:
        """Extract vocabulary from lyrics using Ollama"""
        prompt = f"""
        You are a French language teacher. I will give you French song lyrics, and I want you to help students learn vocabulary from them.

        Instructions:
        1. Identify 5-10 important French words or phrases from the lyrics
        2. For each word:
           - Provide the English translation
           - Include the exact line from the lyrics where it appears
        3. Format each word EXACTLY like this, one per line:
           word | translation | context
        4. Do not include any other text in your response

        Example format:
        danser | to dance | Je danse avec le vent
        coeur | heart | Mon coeur bat pour toi

        Here are the lyrics to analyze:
        {lyrics}
        """
        
        try:
            print("Sending prompt to Ollama...")
            response = self._call_ollama(prompt)
            print(f"Ollama response:\n{response}")
            
            # Parse response into vocabulary items
            vocab_items = []
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            
            for line in lines:
                if '|' not in line:
                    continue
                    
                # Split on | and clean up each part
                parts = [p.strip() for p in line.split('|')]
                
                # Only process lines with exactly 3 parts
                if len(parts) == 3:
                    word, translation, context = parts
                    
                    # Basic validation
                    if word and translation and context:
                        vocab_items.append(
                            VocabularyItem(
                                word=word,
                                translation=translation,
                                context=context
                            )
                        )
            
            print(f"Extracted {len(vocab_items)} vocabulary items")
            return vocab_items
            
        except Exception as e:
            print(f"Error extracting vocabulary: {str(e)}")
            return []
