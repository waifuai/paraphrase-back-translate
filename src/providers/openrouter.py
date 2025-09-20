"""
OpenRouter translation provider implementation.
"""

import logging
import aiohttp
import json
from typing import Optional, List, Tuple, Dict, Any
import asyncio

from .base import TranslationProvider, TranslationRequest, TranslationResponse

# Configure logging for this module
logger = logging.getLogger(__name__)


class OpenRouterProvider(TranslationProvider):
    """
    OpenRouter translation provider.

    Uses the OpenRouter API to provide translation services through various models.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            model: Default model to use (e.g., "deepseek/deepseek-chat-v3")
        """
        super().__init__(api_key, model)
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "openrouter"

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._close_session()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self._session

    async def _close_session(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate text using OpenRouter API.

        Args:
            request: Translation request details

        Returns:
            Translation response with translated text
        """
        try:
            session = await self._ensure_session()

            # Apply rate limiting if available
            from ..rate_limiter import wait_for_rate_limit
            waited = wait_for_rate_limit()
            if waited:
                logger.info(f"Rate limit applied before OpenRouter API call")

            # Prepare the request payload
            payload = self._build_payload(request)

            logger.info(f"Sending translation request to OpenRouter API using model: {payload['model']}")

            # Make the API call
            async with session.post(f"{self.BASE_URL}/chat/completions", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    translated_text = self._extract_translation(result, request)

                    if translated_text:
                        logger.info("OpenRouter translation completed successfully")
                        return TranslationResponse(
                            translated_text=translated_text,
                            success=True,
                            model_used=payload['model']
                        )
                    else:
                        return TranslationResponse(
                            translated_text="",
                            success=False,
                            error_message="OpenRouter API returned empty response",
                            model_used=payload['model']
                        )
                else:
                    error_text = await response.text()
                    error_msg = f"OpenRouter API error (status {response.status}): {error_text}"
                    logger.error(error_msg)
                    return TranslationResponse(
                        translated_text="",
                        success=False,
                        error_message=error_msg,
                        model_used=payload['model']
                    )

        except aiohttp.ClientError as e:
            error_msg = f"OpenRouter API connection error: {str(e)}"
            logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                success=False,
                error_message=error_msg,
                model_used=self.get_model_name(request.model)
            )
        except Exception as e:
            error_msg = f"OpenRouter translation error: {str(e)}"
            logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                success=False,
                error_message=error_msg,
                model_used=self.get_model_name(request.model)
            )

    def _build_payload(self, request: TranslationRequest) -> Dict[str, Any]:
        """
        Build the API payload for OpenRouter.

        Args:
            request: Translation request

        Returns:
            Dictionary containing the API payload
        """
        source_lang_name = _get_language_name(request.source_lang)
        target_lang_name = _get_language_name(request.target_lang)

        messages = [
            {
                "role": "user",
                "content": f"Translate the following {source_lang_name} text to {target_lang_name}:\n\n{request.text}\n\nProvide only the translation without any additional comments or explanations."
            }
        ]

        return {
            "model": self.get_model_name(request.model),
            "messages": messages,
            "temperature": 0.1,  # Low temperature for consistent translations
            "max_tokens": 1000
        }

    def _extract_translation(self, response_data: Dict[str, Any], request: TranslationRequest) -> Optional[str]:
        """
        Extract translation text from OpenRouter response.

        Args:
            response_data: API response data
            request: Original translation request

        Returns:
            Extracted translation text or None
        """
        try:
            choices = response_data.get("choices", [])
            if not choices:
                logger.warning("No choices found in OpenRouter response")
                return None

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()

            if content:
                logger.info("OpenRouter translation extracted successfully")
                return content
            else:
                logger.warning("Empty content in OpenRouter response message")
                return None

        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"Error parsing OpenRouter response: {e}")
            return None

    def get_supported_languages(self) -> List[Tuple[str, str]]:
        """
        Get supported language pairs for OpenRouter.

        OpenRouter supports many languages through different models.
        We'll return a comprehensive list of common language pairs.

        Returns:
            List of supported language pairs as (source, target) tuples
        """
        # Common languages supported by most OpenRouter models
        languages = ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]
        supported_pairs = []

        for source in languages:
            for target in languages:
                if source != target:
                    supported_pairs.append((source, target))

        return supported_pairs

    async def validate_connection(self) -> bool:
        """
        Validate connection to OpenRouter API.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            session = await self._ensure_session()

            # Simple test request
            test_request = TranslationRequest(
                text="Hello",
                source_lang="en",
                target_lang="fr",
                model=self.get_model_name()
            )

            result = await self.translate(test_request)
            await self._close_session()  # Clean up test session

            return result.success

        except Exception as e:
            logger.error(f"OpenRouter connection validation failed: {e}")
            return False


def _get_language_name(lang_code: str) -> str:
    """
    Get full language name from language code.

    Args:
        lang_code: ISO language code

    Returns:
        Full language name
    """
    language_names = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ru": "Russian",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi"
    }

    return language_names.get(lang_code.lower(), lang_code.upper())