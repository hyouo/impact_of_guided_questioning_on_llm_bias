import google.generativeai as genai
import time
from ..config import config
from google.api_core import exceptions
from .base_provider import BaseProvider

class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class GeminiProvider(BaseProvider):
    """
    LLM provider implementation for Google's Gemini models.
    """
    def __init__(self, model_name: str):
        if not config.GEMINI_API_KEY:
            raise APIError("GEMINI_API_KEY is not set in the .env file.")

        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def get_response(self, prompt_text: str) -> str:
        """
        Sends a prompt to the Gemini API and returns the response.
        Implements retry logic for transient errors.
        """
        for attempt in range(config.API_MAX_RETRIES):
            try:
                response = self.model.generate_content(prompt_text)
                if not response.candidates:
                    raise APIError(f"API returned an empty response (Attempt {attempt + 1}/{config.API_MAX_RETRIES})")

                return response.text.strip()

            except exceptions.GoogleAPICallError as e:
                status_code = getattr(e, 'code', None)
                error_msg = f"Gemini API call failed (Attempt {attempt + 1}/{config.API_MAX_RETRIES})"
                if status_code:
                    error_msg += f" with status code: {status_code}"
                else:
                    error_msg += f": {e}"

                print(error_msg)
                if attempt < config.API_MAX_RETRIES - 1:
                    time.sleep(config.API_RETRY_DELAY_SECONDS)
                else:
                    raise APIError(error_msg, status_code=status_code)
            except Exception as e:
                error_msg = f"An unexpected error occurred (Attempt {attempt + 1}/{config.API_MAX_RETRIES}): {e}"
                print(error_msg)
                if attempt < config.API_MAX_RETRIES - 1:
                    time.sleep(config.API_RETRY_DELAY_SECONDS)
                else:
                    raise APIError(error_msg)
        return "" # Should not be reached