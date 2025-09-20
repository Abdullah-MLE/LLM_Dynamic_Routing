from typing import Dict, List
from .base import BaseModel


class MockModel(BaseModel):
    def __init__(self):
        self.models = {
            "simple": "mock-simple",
            "medium": "mock-medium",
            "advanced": "mock-advanced"
        }
    
    def generate(self, prompt: str, model_level: str = "simple") -> str:
        responses = {
            "simple": f"Simple mock response for: {prompt[:30]}...",
            "medium": f"Medium mock response with more detail for: {prompt[:30]}...",
            "advanced": f"Advanced mock response with comprehensive analysis for: {prompt[:30]}..."
        }
        return responses.get(model_level, "Unknown model level")
    
    def list_models(self) -> List[Dict[str, str]]:
        return [{"level": k, "name": v} for k, v in self.models.items()]
    
    def get_model_name(self, level: str) -> str:
        return self.models.get(level, "mock-simple")