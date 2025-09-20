"""
Gemini translation provider implementation.
"""

import logging
from typing import Optional, List, Tuple
from google import genai

from .base import TranslationProvider, TranslationRequest, TranslationResponse

# Configure logging for this module
logger = logging.getLogger(__name__)


class GeminiProvider(TranslationProvider):
    """
    Google Gemini translation provider.

    Uses the official Google GenAI SDK to provide translation services.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the Gemini provider.

        Args:
            api_key: Google Gemini API key
            model: Default Gemini model to use
        """
        super().__init__(api_key, model)
        self._client: Optional[genai.Client] = None

    @property
    def provider_name(self) -> str:
        """Get the provider name."""
        return "gemini"

    def _get_client(self) -> genai.Client:
        """Get or create the Gemini client."""
        if self._client is None:
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise
        return self._client

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate text using Google Gemini.

        Args:
            request: Translation request details

        Returns:
            Translation response with translated text
        """
        try:
            client = self._get_client()

            # Apply rate limiting if available
            from ..rate_limiter import wait_for_rate_limit
            waited = wait_for_rate_limit()
            if waited:
                logger.info(f"Rate limit applied before Gemini API call")

            # Construct the prompt
            prompt = self._build_prompt(request)

            # Determine model to use
            model_name = self.get_model_name(request.model)

            logger.info(f"Sending translation request to Gemini API using model: {model_name}")

            # Make the API call
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            # Extract the translation
            translated_text = self._extract_translation(response, request)

            if translated_text:
                logger.info("Gemini translation completed successfully")
                return TranslationResponse(
                    translated_text=translated_text,
                    success=True,
                    model_used=model_name
                )
            else:
                logger.error("Gemini API returned empty response")
                return TranslationResponse(
                    translated_text="",
                    success=False,
                    error_message="Gemini API returned empty response",
                    model_used=model_name
                )

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            logger.error(error_msg)
            return TranslationResponse(
                translated_text="",
                success=False,
                error_message=error_msg,
                model_used=self.get_model_name(request.model)
            )

    def _build_prompt(self, request: TranslationRequest) -> str:
        """
        Build the translation prompt for Gemini.

        Args:
            request: Translation request

        Returns:
            Formatted prompt string
        """
        source_lang_name = _get_language_name(request.source_lang)
        target_lang_name = _get_language_name(request.target_lang)

        return f"""Translate the following {source_lang_name} text to {target_lang_name}:

{request.text}

Provide only the translation without any additional comments or explanations."""

    def _extract_translation(self, response, request: TranslationRequest) -> Optional[str]:
        """
        Extract translation text from Gemini response.

        Args:
            response: Gemini API response
            request: Original translation request

        Returns:
            Extracted translation text or None
        """
        try:
            # Try the primary response field
            if hasattr(response, "output_text") and response.output_text:
                return response.output_text.strip()

            # Fallback for different response formats
            text_candidate = getattr(response, "text", "") or getattr(response, "candidates", "")
            if text_candidate:
                translation = str(text_candidate).strip()
                logger.info(f"Gemini translation extracted via fallback field")
                return translation

            logger.warning(f"No text content found in Gemini response")
            return None

        except Exception as e:
            logger.error(f"Error extracting translation from Gemini response: {e}")
            return None

    def get_supported_languages(self) -> List[Tuple[str, str]]:
        """
        Get supported language pairs for Gemini.

        Gemini supports a wide range of languages, but we'll focus on
        the most commonly used pairs for this application.

        Returns:
            List of supported language pairs as (source, target) tuples
        """
        # Gemini supports many languages, but we'll focus on common pairs
        languages = ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja", "ko"]
        supported_pairs = []

        for source in languages:
            for target in languages:
                if source != target:
                    supported_pairs.append((source, target))

        return supported_pairs

    def validate_connection(self) -> bool:
        """
        Validate connection to Gemini API.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            client = self._get_client()
            # Try a simple request to validate the connection
            # We'll use a minimal test prompt
            test_request = TranslationRequest(
                text="Hello",
                source_lang="en",
                target_lang="fr",
                model=self.get_model_name()
            )

            # For validation, we can use a synchronous approach
            # since this is just a connection test
            import asyncio
            result = asyncio.run(self.translate(test_request))

            return result.success

        except Exception as e:
            logger.error(f"Gemini connection validation failed: {e}")
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
        "ko": "Korean"
    }

    return language_names.get(lang_code.lower(), lang_code.upper())