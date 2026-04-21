"""
Configuration management for the back-translation project using OpenRouter API.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging
from pathlib import Path

# Configure logging for this module
logger = logging.getLogger(__name__)

class TypeOfTranslation(Enum):
    """Represents the direction of translation."""
    en_to_fr = 1
    fr_to_en = 2

DEFAULT_OPENROUTER_MODEL = "openrouter/free"

MODEL_FILE_OPENROUTER = Path.home() / ".model-openrouter"

@dataclass
class Config:
    """Holds all configuration parameters for the back-translation process."""
    cycles: int
    initial_translation_type_str: str  # "en_to_fr" or "fr_to_en"
    pooling_dir: str
    log_dir: str
    local_base_dir: str = "."
    model_name: Optional[str] = None  # Model override

    # --- Derived properties ---
    initial_translation_type: TypeOfTranslation = field(init=False)
    api_key: str = field(init=False)
    resolved_model_name: str = field(init=False)

    def __post_init__(self):
        """Calculate derived properties and load API key after initialization."""
        # Determine initial translation type
        if self.initial_translation_type_str == "en_to_fr":
            self.initial_translation_type = TypeOfTranslation.en_to_fr
        elif self.initial_translation_type_str == "fr_to_en":
            self.initial_translation_type = TypeOfTranslation.fr_to_en
        else:
            raise ValueError(f"Invalid translation_type: {self.initial_translation_type_str}")

        # Resolve model name with dotfile fallback
        self.resolved_model_name = self._resolve_model_name()

        # Load OpenRouter API Key
        self._load_api_key()

    # --- Provider/model resolution ---

    def _resolve_model_name(self) -> str:
        """
        Resolve the model name based on:
        1) Explicit model_name if provided
        2) ~/.model-openrouter file
        3) Default 'openrouter/free'

        Returns:
            Resolved model name string
        """
        # 1) Explicit override takes precedence
        if self.model_name and str(self.model_name).strip():
            return str(self.model_name).strip()

        # 2) Model file
        try:
            if MODEL_FILE_OPENROUTER.is_file():
                content = MODEL_FILE_OPENROUTER.read_text(encoding="utf-8").strip()
                if content:
                    return content
        except Exception as e:
            logger.debug(f"Failed to read model file {MODEL_FILE_OPENROUTER}: {e}")

        # 3) Default
        return DEFAULT_OPENROUTER_MODEL

    def _load_api_key(self) -> None:
        """
        Loads the OpenRouter API key with the following precedence:
        1) Environment variable OPENROUTER_API_KEY
        2) Fallback: contents of ~/.api-openrouter

        Raises:
            FileNotFoundError: If API key file is not found and no environment variable is set
            ValueError: If API key file exists but is empty
            OSError: If API key file cannot be read
        """
        # Try environment variable first
        env_key = os.getenv("OPENROUTER_API_KEY")
        if env_key and env_key.strip():
            self.api_key = env_key.strip()
            logger.info("OpenRouter API key loaded from environment variable.")
            return

        # Fall back to file
        expanded_path = os.path.expanduser("~/.api-openrouter")
        logger.info(f"Attempting to load OpenRouter API key from: {expanded_path}")

        try:
            with open(expanded_path, "r", encoding='utf-8') as f:
                api_key_content = f.read().strip()
            if not api_key_content:
                raise ValueError("API key file is empty.")
            self.api_key = api_key_content
            logger.info("OpenRouter API key loaded successfully from file.")
        except FileNotFoundError:
            logger.error(f"Error: API key not found in environment and file not found at {expanded_path}")
            raise FileNotFoundError(
                f"API key not found in environment and file not found at {expanded_path}. "
                "Set OPENROUTER_API_KEY, or create the key file."
            ) from None
        except ValueError:
            logger.error(f"Error: API key file is empty: {expanded_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading API key file {expanded_path}: {e}")
            raise OSError(f"Cannot read API key file '{expanded_path}': {e}") from e

    # --- Path generation methods ---

    def _get_pool_name(self, translation_type: TypeOfTranslation) -> str:
        """
        Helper to get the base pool name for a given translation direction.
        """
        return "input_pool" if translation_type == TypeOfTranslation.en_to_fr else "french_pool"

    def get_input_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the input directory for the given translation type.
        """
        return os.path.join(self.pooling_dir, self._get_pool_name(translation_type))

    def get_output_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the output directory for the given translation type.
        """
        output_pool = "french_pool" if translation_type == TypeOfTranslation.en_to_fr else "output_pool"
        return os.path.join(self.pooling_dir, output_pool)

    def get_completed_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the completed directory for the given translation type.
        """
        completed_pool = f"{self._get_pool_name(translation_type)}_completed"
        return os.path.join(self.pooling_dir, completed_pool)

    @property
    def log_filepath(self) -> str:
        """
        Returns the absolute path to the log file.
        Creates the log directory if it doesn't exist.
        """
        local_log_dir = os.path.join(self.local_base_dir, self.log_dir)

        try:
            os.makedirs(local_log_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create log directory '{local_log_dir}': {e}")
            raise

        return os.path.join(local_log_dir, "backtranslate.log")
