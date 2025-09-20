from router.rules import classify_query
from router.cache import Cache
from models.gemini_models import GeminiModels
from models.mock_model import MockModel
from config import Config


class QueryRouter:

    def __init__(self):
        self.config = Config()
        self.cache = Cache()

        # Select model provider based on config
        if self.config.MODEL_PROVIDER == "gemini":
            self.model = GeminiModels()
        elif self.config.MODEL_PROVIDER == "mock":
            self.model = MockModel()
        else:
            raise ValueError(
                "Unknown model provider: ",
                self.config.MODEL_PROVIDER
            )

    def route_query_and_return_response(self, query, use_cache=True):
        cached_result = self._check_cache(query, use_cache)
        if cached_result:
            return cached_result

        complexity = classify_query(query)
        model_level = complexity
        # send the model level based on complexity and return the model used
        # in case of fallback
        response, model = self._get_response_with_fallback(
            query,
            model_level,
            complexity
        )

        self._cache_response(
            query,
            response,
            model,
            complexity,
            use_cache
        )

        return {
            "query": query,
            "response": response,
            "complexity": complexity,
            "model_name": model,
            "cached": False
        }

    def _check_cache(self, query: str, use_cache: bool):
        if not use_cache or not self.cache.enabled:
            return None

        cached_data = self.cache.get(query)
        if cached_data:
            return {
                "query": query,
                "response": cached_data["response"],
                "complexity": cached_data['complexity'],
                "model_name": cached_data["model"],
                "cached": True,
                "timestamp": cached_data["timestamp"]
            }
        return None

    def _cache_response(self, query: str, response: str, model_name: str,
                        complexity: str, use_cache: bool):
        if use_cache and self.cache.enabled:
            self.cache.set(
                query=query,
                response=response,
                model=model_name,
                complexity=complexity
            )

    def _get_response_with_fallback(self, query: str, model_level: str,
                                    complexity: str, retries: int = 0):
        response = self.model.generate(query, model_level)

        # Check if response is valid
        if self._is_response_valid(response):
            # If valid, return response and model name
            return response, self._get_model_name(model_level)

        # If not valid, check if fallback is enabled and retries are left
        elif (
            self.config.FALLBACK_ENABLED
            and retries < self.config.MAX_RETRIES
        ):
            return self._try_fallback(query, model_level, complexity, retries)

        # If no fallback, return the (invalid) response and model name
        return response, self._get_model_name(model_level)

    def _is_response_valid(self, response: str):
        if not response or len(response.strip()) < 5:
            return False

        # Check if response starts with any invalid phrases
        for phrase in self.config.INVALID_PHRASES:
            if response.startswith(phrase):
                return False

        return True

    def _try_fallback(self, query: str, current_level: str,
                      complexity: str, retries: int):
        upgrade_map = {
            "simple": "medium",
            "medium": "advanced"
        }

        next_level = upgrade_map.get(current_level)
        if not next_level:
            raise Exception(f"No fallback available for {current_level} model")

        print(f"Upgrading from {current_level} to {next_level} model...")
        return self._get_response_with_fallback(
            query,
            next_level,
            complexity,
            retries + 1
        )

    def _get_model_name(self, model_level: str):
        model_names = {
            "simple": self.config.SIMPLE_MODEL,
            "medium": self.config.MEDIUM_MODEL,
            "advanced": self.config.ADVANCED_MODEL
        }
        return model_names.get(model_level, self.config.SIMPLE_MODEL)


if __name__ == "__main__":
    router = QueryRouter()
    test_query = "What is the capital of France?"
    result = router.route_query_and_return_response(test_query)
    print(result)
