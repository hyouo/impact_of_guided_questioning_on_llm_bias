import google.generativeai as genai
import time
import json
from .config import config
from google.api_core import exceptions # New import

class APIError(Exception):
    """Custom exception for API-related errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class LLMAPI:
    def __init__(self, model_name):
        if not config.GEMINI_API_KEY:
            raise APIError("GEMINI_API_KEY 未设置。请在 .env 文件中配置您的 API 密钥。")
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def _call_api_with_retry(self, prompt_content, is_json_output=False):
        """
        Internal method to call the Gemini API with retry logic.
        """
        for attempt in range(config.API_MAX_RETRIES):
            try:
                response = self.model.generate_content(prompt_content)
                # Check if response is empty or has errors
                if not response.candidates:
                    raise APIError(f"API 返回空响应或无候选内容 (尝试 {attempt + 1}/{config.API_MAX_RETRIES})")
                
                text_output = response.text.strip()
                
                if is_json_output:
                    try:
                        return json.loads(text_output)
                    except json.JSONDecodeError:
                        raise APIError(f"API 返回的不是有效的 JSON 格式 (尝试 {attempt + 1}/{config.API_MAX_RETRIES}): {text_output[:200]}...")
                
                return text_output

            except exceptions.GoogleAPICallError as e: # Catch specific API call errors
                status_code = None
                # Attempt to extract HTTP status code if available
                if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                    status_code = e.response.status_code
                elif hasattr(e, 'code'): # For gRPC status codes
                    # grpc.StatusCode is an enum, its value is a tuple (int, str) or just int
                    status_code = e.code.value[0] if isinstance(e.code.value, tuple) else e.code.value 
                
                error_msg = f"API 调用失败 (尝试 {attempt + 1}/{config.API_MAX_RETRIES})"
                if status_code:
                    error_msg += f", 状态码: {status_code}"
                else:
                    error_msg += f": {e}" # Fallback to full exception if no code

                print(error_msg)
                if attempt < config.API_MAX_RETRIES - 1:
                    time.sleep(config.API_RETRY_DELAY_SECONDS)
                else:
                    raise APIError(error_msg, status_code=status_code) # Raise custom APIError with code
            except Exception as e: # Catch other general exceptions
                error_msg = f"API 调用失败 (尝试 {attempt + 1}/{config.API_MAX_RETRIES}): {e}"
                print(error_msg)
                if attempt < config.API_MAX_RETRIES - 1:
                    time.sleep(config.API_RETRY_DELAY_SECONDS)
                else:
                    raise APIError(error_msg) # Raise custom APIError without code