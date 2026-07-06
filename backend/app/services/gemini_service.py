# =====================================================================
# FILE: backend/app/services/gemini_service.py
# DESCRIPTION: Primary Gemini service with robust fallback to NVIDIA.
# =====================================================================

import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

# Configure the Gemini API client
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        logger.info("Gemini API client configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API client: {e}")
else:
    logger.warning("GEMINI_API_KEY is not set. Gemini API calls will fallback to NVIDIA.")


def ask_gemini(prompt: str, temperature: float = 0.2) -> str:
    """
    Queries Google Gemini API (gemini-2.5-flash) first.
    If it fails or if the API key is missing, falls back to the NVIDIA API.
    """
    if settings.GEMINI_API_KEY:
        try:
            logger.info("Attempting to query Google Gemini (gemini-2.5-flash)...")
            generation_config = genai.types.GenerationConfig(
                temperature=temperature
            )
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt, generation_config=generation_config)
            if response and response.text:
                logger.info("Google Gemini query succeeded.")
                return response.text.strip()
            else:
                logger.warning("Google Gemini returned empty response. Falling back to NVIDIA.")
        except Exception as e:
            logger.error(f"Google Gemini query failed: {e}. Falling back to NVIDIA.")
    else:
        logger.info("GEMINI_API_KEY is not set. Directly falling back to NVIDIA.")

    # Fallback to NVIDIA API
    try:
        from app.services.nvidia_service import generate_text
        logger.info("Invoking NVIDIA generate_text fallback.")
        return generate_text(prompt, allow_legacy_fallback=False, temperature=temperature)
    except Exception as e:
        logger.error(f"NVIDIA generate_text fallback also failed: {e}")
        return f"Error: {e}"


# Model stub class to support streaming and backward compatibility
class _ModelStub:
    def generate_content(self, prompt, stream=False, generation_config=None):
        if stream:
            return _StreamStub(prompt, generation_config=generation_config)
        
        # Non-streaming
        temp = 0.7
        if generation_config:
            if hasattr(generation_config, "temperature"):
                temp = generation_config.temperature
            elif isinstance(generation_config, dict):
                temp = generation_config.get("temperature", 0.7)
        text = ask_gemini(prompt, temperature=temp)
        return _ResponseStub(text)


class _ResponseStub:
    def __init__(self, text):
        self.text = text


class _StreamStub:
    def __init__(self, prompt, generation_config=None):
        self._prompt = prompt
        self._generation_config = generation_config

    def __iter__(self):
        temp = 0.7
        if self._generation_config:
            if hasattr(self._generation_config, "temperature"):
                temp = self._generation_config.temperature
            elif isinstance(self._generation_config, dict):
                temp = self._generation_config.get("temperature", 0.7)

        if settings.GEMINI_API_KEY:
            try:
                logger.info("Attempting to query Google Gemini Stream (gemini-2.5-flash)...")
                generation_config = genai.types.GenerationConfig(
                    temperature=temp
                )
                model = genai.GenerativeModel("gemini-2.5-flash")
                response_stream = model.generate_content(
                    self._prompt, 
                    stream=True, 
                    generation_config=generation_config
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield _ResponseStub(chunk.text)
                logger.info("Google Gemini Stream completed successfully.")
                return
            except Exception as e:
                logger.error(f"Google Gemini Stream failed: {e}. Falling back to NVIDIA stream.")
        else:
            logger.info("GEMINI_API_KEY is not set. Directly falling back to NVIDIA stream.")

        # Fallback to NVIDIA stream
        try:
            from app.services.nvidia_service import generate_text_stream
            logger.info("Invoking NVIDIA generate_text_stream fallback.")
            for chunk in generate_text_stream(self._prompt, allow_legacy_fallback=False, temperature=temp):
                yield _ResponseStub(chunk)
        except Exception as e:
            logger.error(f"NVIDIA generate_text_stream fallback also failed: {e}")
            yield _ResponseStub(f"Error: {e}")


model = _ModelStub()
