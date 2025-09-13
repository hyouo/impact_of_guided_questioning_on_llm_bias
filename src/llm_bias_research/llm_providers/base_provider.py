from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers.
    It defines the interface that all provider implementations must follow.
    """

    @abstractmethod
    def get_response(self, prompt_text: str) -> str:
        """
        Sends a prompt to the LLM and returns the text response.

        Args:
            prompt_text: The text of the prompt to send to the model.

        Returns:
            The raw text response from the model.
        """
        pass
