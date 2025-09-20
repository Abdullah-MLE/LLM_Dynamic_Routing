from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class QueryResponse:
    """Unified response format for all model operations"""
    query: str
    response: str
    complexity: str
    model_name: str
    cached: bool = False
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "response": self.response,
            "complexity": self.complexity,
            "final_model": self.model_name,
            "cached": self.cached,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryResponse':
        """Create from dictionary format"""
        return cls(
            query=data["query"],
            response=data["response"],
            complexity=data["complexity"],
            model_name=data.get("final_model", data.get("model", "unknown")),
            cached=data.get("cached", False),
            timestamp=data.get("timestamp", 0.0)
        )
