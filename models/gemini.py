from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from dotenv import load_dotenv
from google import genai
import os
from .base import BaseModel

from config import config

# Load environment variables
load_dotenv()


@dataclass
class ModelInfo:
    name: str
    supports_thinking: bool
    max_tokens: int

class GeminiModels(BaseModel):
    def __init__(self):
        self._validate_api_key()
        self.client = self._create_client()
        self.models = self._setup_models()
    
    def _validate_api_key(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
    
    def _create_client(self):
        return genai.Client(api_key=self.api_key)
    
    def _setup_models(self):
        return {
            "simple": ModelInfo(name=config.SIMPLE_MODEL, supports_thinking=False, max_tokens=2048),
            "medium": ModelInfo(name=config.MEDIUM_MODEL, supports_thinking=False, max_tokens=4096),
            "advanced": ModelInfo(name=config.ADVANCED_MODEL, supports_thinking=True, max_tokens=8192)
        }
    
    def _get_model_info(self, model_level: str):
        if model_level not in self.models:
            raise ValueError(f"Unknown model level: {model_level}")
        return self.models[model_level]
    
    def generate(self, prompt: str, model_level: str):
        model_info = self._get_model_info(model_level)
        
        response = self.client.models.generate_content(
            model=model_info.name,
            contents=prompt
        )
        
        return response.text
    
    def list_models(self):
        result = []
        for level, info in self.models.items():
            model_dict = {
                "level": level,
                "name": info.name
            }
            result.append(model_dict)
        return result
    
    def get_model_name(self, level: str):
        model_info = self._get_model_info(level)
        return model_info.name
    
    def Print_all_available_Gemini_models(self):
        models = self.client.models.list()
        print("Available Gemini models:")
        for model in models:
            print("-", model.name)


if __name__ == "__main__":
    gemini = GeminiModels()
    print("Testing Gemini model...")
    response = gemini.generate("What is AI?", "simple")
    print(f"Response: {response}")