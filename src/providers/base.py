"""
Base provider interface for translation services.
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class TranslationRequest:
    """Request data for translation."""
    text: str
    source_lang: str
    target_lang: str
    model: Optional[str] = None


@dataclass
class TranslationResponse:
    """Response data from translation service."""
    translated_text: str
    success: bool = True
    error_message: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None


class TranslationProvider(ABC):
    """
    Abstract base class for translation providers.

    This defines the interface that all translation providers must implement,
    allowing for easy swapping between different translation services.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the provider.

        Args:
            api_key: API key for the translation service
            model: Default model to use for translations
        """
        self.api_key = api_key
        self.default_model = model

    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate text from source language to target language.

        Args:
            request: Translation request details

        Returns:
            Translation response with translated text or error details

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement translate()")

    @abstractmethod
    def get_supported_languages(self) -> list:
        """
        Get list of supported language pairs.

        Returns:
            List of supported language pairs as tuples (source, target)
        """
        raise NotImplementedError("Subclasses must implement get_supported_languages()")

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the provider can connect to the service.

        Returns:
            True if connection is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate_connection()")

    def get_model_name(self, requested_model: Optional[str] = None) -> str:
        """
        Get the model name to use for translation.

        Args:
            requested_model: Specific model requested, or None for default

        Returns:
            Model name to use
        """
        return requested_model or self.default_model or "default"

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider."""
        raise NotImplementedError("Subclasses must implement provider_name")