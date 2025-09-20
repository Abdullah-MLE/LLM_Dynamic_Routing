from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.MODEL_PROVIDER = "gemini"  # Options: "gemini", "mock"
        self.MODEL_LEVELS = ["simple", "medium", "advanced"]

        self.SIMPLE_MODEL = "gemini-1.5-flash-latest"
        self.MEDIUM_MODEL = "gemini-2.5-flash"
        self.ADVANCED_MODEL = "gemini-2.5-pro"

        self.MAX_SIMPLE_LENGTH = 50
        self.MAX_MEDIUM_LENGTH = 200

        self.CACHE_ENABLED = True
        self.FALLBACK_ENABLED = True
        self.MAX_RETRIES = 2

        self.COMPLEX_KEYWORDS = [
            "explain", "analyze", "compare", "contrast", "evaluate",
            "synthesize", "critique", "interpret", "discuss", "theorize"
        ]
        self.SIMPLE_KEYWORDS = [
            "what", "when", "where", "who", "how", "define", "list"
        ]


config = Config()
