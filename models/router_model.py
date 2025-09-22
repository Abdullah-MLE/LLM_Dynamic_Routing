from dotenv import load_dotenv
from google import genai
from google.genai import types
from .base import BaseModel
from config import Config

# Load environment variables
load_dotenv()


class RouterModel(BaseModel):
    def __init__(self):
        config = Config()
        self.client = genai.Client()
        self.model = config.LLM_ROUTE_MODEL

    def generate(self, prompt: str, model_level: str):
        pass

    def classify_difficulty(self, question: str):
        prompt = f"""Classify this question's difficulty level.
                    Respond with ONLY ONE WORD: simple, medium, advanced
                    Question: {question}
                    Classification:
                """

        # Configure generation for speed and brevity
        response = self.client.models.generate_content(
            contents=prompt,
            model=self.model,
            config=types.GenerateContentConfig(
                temperature=0.1
            )
        )

        difficulty = response.text.strip().lower()

        return difficulty


if __name__ == "__main__":
    model = RouterModel()
    print("Testing Gemini model...")
    response = model.classify_difficulty("What is AI?")
    print(f"Response: {response}")
