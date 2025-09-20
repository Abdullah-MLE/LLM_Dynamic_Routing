from router.rules import classify_query
from router.cache import Cache
from models.gemini import GeminiModels
from models.mock import MockModel
from models.response import QueryResponse
from config import config


class QueryRouter:

    def __init__(self):
        self.cache = Cache()

        # Select model provider based on config
        if config.MODEL_PROVIDER == "gemini":
            self.model = GeminiModels()
        elif config.MODEL_PROVIDER == "mock":
            self.model = MockModel()
        else:
            raise ValueError("Unknown model provider: ", config.MODEL_PROVIDER)

    def route_query_and_return_response(self, query, use_cache=True):
        cached_result = self._check_cache(query, use_cache)
        if cached_result:
            return cached_result

        complexity = classify_query(query)
        model_level = complexity
        response, final_model = self._get_response_with_fallback(
            query,
            model_level,
            complexity
        )

        self._cache_response(
            query,
            response,
            final_model,
            complexity,
            use_cache
        )

        return QueryResponse(
            query=query,
            response=response,
            complexity=complexity,
            model_name=final_model,
            cached=False
        )

    def _check_cache(self, query: str, use_cache: bool):
        if not use_cache or not self.cache.is_enabled():
            return None

        cached_data = self.cache.get(query)
        if cached_data:
            return QueryResponse(
                query=query,
                response=cached_data["response"],
                complexity=cached_data['complexity'],
                model_name=cached_data["model"],
                cached=True,
                timestamp=cached_data.get("timestamp", 0.0)
            )
        return None

    def _cache_response(self, query: str, response: str, model_name: str, complexity: str, use_cache: bool):
        if use_cache and self.cache.is_enabled():
            self.cache.set(
                query=query,
                response=response,
                model=model_name,
                complexity=complexity
            )

    def _get_response_with_fallback(self, query: str, model_level: str, complexity: str, retries: int = 0):
        try:
            response = self.model.generate(query, model_level)

            if self._is_response_valid(response):
                return response, self._get_model_name(model_level)

            if config.FALLBACK_ENABLED and retries < config.MAX_RETRIES:
                return self._try_fallback(query, model_level, complexity, retries)

            return response, self._get_model_name(model_level)

        except Exception as e:
            if config.FALLBACK_ENABLED and retries < config.MAX_RETRIES:
                print(f"Error with {model_level} model: {str(e)}. Trying fallback...")
                return self._try_fallback(query, model_level, complexity, retries)

            raise Exception(f"All models failed. Last error: {str(e)}")

    def _is_response_valid(self, response: str):
        return len(response.strip()) > 0

    def _try_fallback(self, query: str, current_level: str, complexity: str, retries: int):
        upgrade_map = {
            "simple": "medium",
            "medium": "advanced"
        }

        next_level = upgrade_map.get(current_level)
        if not next_level:
            raise Exception(f"No fallback available for {current_level} model")

        print(f"Upgrading from {current_level} to {next_level} model...")
        return self._get_response_with_fallback(query, next_level, complexity, retries + 1)

    def _get_model_name(self, model_level: str):
        model_names = {
            "simple": config.SIMPLE_MODEL,
            "medium": config.MEDIUM_MODEL,
            "advanced": config.ADVANCED_MODEL
        }
        return model_names.get(model_level, config.SIMPLE_MODEL)


if __name__ == "__main__":
    router = QueryRouter()
    test_query = "What is the capital of France?"
    result = router.route_query_and_return_response(test_query)
    print(result)
