from abc import ABC, abstractmethod


class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, model_level: str):
        pass

    @abstractmethod
    def get_model_name(self, level: str):
        pass
