import time
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from config import Config


class Cache:
    def __init__(self):
        config = Config()
        self.enabled = config.CACHE_ENABLED
        self.cache_dir = os.path.join("data", "cache")
        self.cache_file = os.path.join(self.cache_dir, "query_cache.json")
        self.memory_cache = {}

        self._ensure_cache_dir()
        self._load_from_file()

    def _ensure_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _load_from_file(self):
        if not self.enabled:
            return

        with open(self.cache_file, 'r', encoding='utf-8') as f:
            self.memory_cache = json.load(f)

    def _save_to_file(self):
        if not self.enabled:
            return

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            # dump(content, file path, space=2, keep non-ASCII chars)
            json.dump(self.memory_cache, f, indent=2, ensure_ascii=False)

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        if query in self.memory_cache:
            cache_record = self.memory_cache[query]
            return {
                "response": cache_record["response"],
                "model": cache_record.get("model", "unknown"),
                "complexity": cache_record.get("complexity", "unknown"),
                "timestamp": cache_record.get("timestamp", 0)
            }

        return None

    def set(self, query, response, model="unknown", complexity="unknown"):
        if not self.enabled:
            return

        self.memory_cache[query] = {
            "query": query,
            "response": response,
            "model": model,
            "complexity": complexity,
            "timestamp": time.time(),
            "date": datetime.now().isoformat(),
            "response_length": len(response)
        }

        self._save_to_file()

    def clear(self):
        self.memory_cache = {}
        if self.enabled and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
