from .base import BaseModel


class MockModel(BaseModel):
    def __init__(self):
        self.models = {
            "simple": "mock-simple",
            "medium": "mock-medium",
            "advanced": "mock-advanced"
        }

    def generate(self, prompt: str, level: str = "simple"):
        text = prompt[:30] + "..."
        return {
            "simple": f"Simple mock response for: {text}",
            "medium": f"Medium mock response with more detail for: {text}",
            "advanced": f"Advanced mock response with comprehensive "
                        f"analysis for: {text}"
        }.get(level, "Unknown model level")

    def get_model_name(self, level: str):
        return self.models.get(level, "mock-simple")
