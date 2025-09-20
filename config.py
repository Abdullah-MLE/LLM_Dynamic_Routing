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

        self.CACHE_ENABLED = False
        self.FALLBACK_ENABLED = True
        self.MAX_RETRIES = 2

        self.COMPLEX_KEYWORDS = [
            "analyze", "compare", "contrast", "evaluate", "critique",
            "interpret", "discuss", "theorize", "synthesize", "examine",
            "investigate", "assess", "review", "debate", "argue",
            "justify", "validate", "criticize", "appraise", "judge"
        ]

        self.SIMPLE_KEYWORDS = [
            "what", "when", "where", "who", "which", "define", "list",
            "name", "find", "show", "tell", "give", "provide",
            "identify", "state", "mention", "recall", "recognize"
        ]

        self.INVALID_PHRASES = [
            "i don't know",
            "i'm not sure",
            "i can't help",
            "i cannot help",
            "i don't have information",
            "i'm unable to",
            "i cannot provide",
            "i don't understand",
            "i can't answer"
        ]
