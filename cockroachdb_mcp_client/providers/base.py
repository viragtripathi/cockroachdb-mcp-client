from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    @abstractmethod
    def run(self, context: dict, input_text: str) -> str:
        """
        Run an inference call against the provider with the given context and input.
        """
        pass
