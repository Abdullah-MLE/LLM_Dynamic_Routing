from abc import ABC, abstractmethod
from typing import Dict, List


class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, model_level: str) -> str:
        pass
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, str]]:
        pass
    
    @abstractmethod
    def get_model_name(self, level: str) -> str:
        pass