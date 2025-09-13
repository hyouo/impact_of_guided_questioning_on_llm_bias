import openai
import time
from ..config import config
from .base_provider import BaseProvider
from .gemini_provider import APIError  # Reusing the same custom error for consistency

class OpenAIProvider(BaseProvider):
    """
    LLM provider implementation for OpenAI's GPT models.
    """
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        if not config.OPENAI_API_KEY:
            raise APIError("OPENAI_API_KEY is not set in the .env file.")

        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model_name = model_name

    def get_response(self, prompt_text: str) -> str:
        """
        Sends a prompt to the OpenAI API and returns the response.
        Implements retry logic for transient errors.
        """
        for attempt in range(config.API_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                if not response.choices:
                    raise APIError(f"API returned an empty response (Attempt {attempt + 1}/{config.API_MAX_RETRIES})")

                return response.choices[0].message.content.strip()

            except openai.APIError as e:
                status_code = e.status_code
                error_msg = f"OpenAI API call failed (Attempt {attempt + 1}/{config.API_MAX_RETRIES})"
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
