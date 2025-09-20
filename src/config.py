"""
Configuration management for the back-translation project using Gemini API.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import logging
from pathlib import Path

# Configure logging for this module
logger = logging.getLogger(__name__)

class TypeOfTranslation(Enum):
    """Represents the direction of translation."""
    en_to_fr = 1
    fr_to_en = 2

DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-chat-v3-0324:free"

MODEL_FILE_GEMINI = Path.home() / ".model-gemini"
MODEL_FILE_OPENROUTER = Path.home() / ".model-openrouter"

class Provider(str, Enum):
    """Supported providers for model selection."""
    openrouter = "openrouter"
    gemini = "gemini"

@dataclass
class Config:
    """Holds all configuration parameters for the back-translation process."""
    cycles: int
    initial_translation_type_str: str  # "en_to_fr" or "fr_to_en"
    pooling_dir: str
    log_dir: str
    local_base_dir: str = "."
    # Back-compat: gemini specific override if no common model provided and provider == gemini
    gemini_model_name: str = DEFAULT_GEMINI_MODEL
    api_key_path: str = "~/.api-gemini"  # Path to the API key file for Gemini
    # New provider and model fields
    provider: Provider = Provider.openrouter  # Default provider switched to OpenRouter
    model_name: Optional[str] = None         # Common model override (applies to any provider)

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
            # This should ideally be caught by argparse choices, but good to have defense
            raise ValueError(f"Invalid translation_type: {self.initial_translation_type_str}")

        # Resolve model name per provider with dotfile fallbacks
        self.resolved_model_name = self._resolve_model_name()

        # Load API Key (Gemini path remains unchanged; translation still uses Gemini SDK)
        self._load_api_key()

    # --- Provider/model resolution ---

    def _resolve_model_name(self) -> str:
        """
        Resolve the model name based on:
        1) Explicit model_name if provided
        2) Provider-specific model file in the user's home directory
           - ~/.model-openrouter for provider=openrouter
           - ~/.model-gemini for provider=gemini
        3) Provider-specific default
        4) Back-compat: if provider=gemini and no explicit/common model, use gemini_model_name field

        Returns:
            Resolved model name string

        Raises:
            ValueError: If resolved model name is empty
        """
        # 1) Explicit override takes precedence
        if self.model_name and str(self.model_name).strip():
            resolved = str(self.model_name).strip()
            if resolved:
                return resolved

        # 2) Provider-specific model files
        model_file: Optional[Path] = None
        if self.provider == Provider.openrouter:
            model_file = MODEL_FILE_OPENROUTER
        elif self.provider == Provider.gemini:
            model_file = MODEL_FILE_GEMINI

        if model_file:
            try:
                if model_file.is_file():
                    content = model_file.read_text(encoding="utf-8").strip()
                    if content:
                        return content
            except Exception as e:
                # Non-fatal; fall through to defaults
                logger.debug(f"Failed to read provider model file {model_file}: {e}")

        # 3) Back-compat for Gemini: prefer gemini_model_name if provider is gemini
        if self.provider == Provider.gemini and (self.gemini_model_name and self.gemini_model_name.strip()):
            return self.gemini_model_name.strip()

        # 4) Provider-specific defaults
        default_model = DEFAULT_OPENROUTER_MODEL if self.provider == Provider.openrouter else DEFAULT_GEMINI_MODEL

        if not default_model:
            raise ValueError(f"No valid model name could be resolved for provider {self.provider.value}")

        return default_model

    def _load_api_key(self) -> None:
        """
        Loads the Gemini API key with the following precedence:
        1) Environment variable GEMINI_API_KEY
        2) Environment variable GOOGLE_API_KEY
        3) Fallback: contents of the file at api_key_path (default ~/.api-gemini)

        Raises:
            FileNotFoundError: If API key file is not found and no environment variable is set
            ValueError: If API key file exists but is empty
            OSError: If API key file cannot be read
        """
        # Try environment variables first
        env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_key and env_key.strip():
            self.api_key = env_key.strip()
            logger.info("Gemini API key loaded from environment variable.")
            return

        # Fall back to file
        expanded_path = os.path.expanduser(self.api_key_path)
        logger.info(f"Attempting to load Gemini API key from: {expanded_path}")

        try:
            with open(expanded_path, "r", encoding='utf-8') as f:
                api_key_content = f.read().strip()
            if not api_key_content:
                raise ValueError("API key file is empty.")
            self.api_key = api_key_content
            logger.info("Gemini API key loaded successfully from file.")
        except FileNotFoundError:
            logger.error(f"Error: API key not found in environment and file not found at {expanded_path}")
            raise FileNotFoundError(
                f"API key not found in environment and file not found at {expanded_path}. "
                "Set GEMINI_API_KEY or GOOGLE_API_KEY, or create the key file."
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

        Args:
            translation_type: The translation direction

        Returns:
            Base pool name string
        """
        return "input_pool" if translation_type == TypeOfTranslation.en_to_fr else "french_pool"

    def get_input_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the input directory for the given translation type.

        Args:
            translation_type: The translation direction

        Returns:
            Absolute path to input directory
        """
        return os.path.join(self.pooling_dir, self._get_pool_name(translation_type))

    def get_output_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the output directory for the given translation type.

        Args:
            translation_type: The translation direction

        Returns:
            Absolute path to output directory
        """
        output_pool = "french_pool" if translation_type == TypeOfTranslation.en_to_fr else "output_pool"
        return os.path.join(self.pooling_dir, output_pool)

    def get_completed_dir(self, translation_type: TypeOfTranslation) -> str:
        """
        Returns the absolute path to the completed directory for the given translation type.

        Args:
            translation_type: The translation direction

        Returns:
            Absolute path to completed directory
        """
        completed_pool = f"{self._get_pool_name(translation_type)}_completed"
        return os.path.join(self.pooling_dir, completed_pool)

    @property
    def log_filepath(self) -> str:
        """
        Returns the absolute path to the log file.

        Creates the log directory if it doesn't exist.

        Returns:
            Absolute path to the log file

        Raises:
            OSError: If log directory cannot be created
        """
        # Uses local_base_dir for log path construction
        local_log_dir = os.path.join(self.local_base_dir, self.log_dir)

        try:
            # Ensure log directory exists before returning path
            os.makedirs(local_log_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create log directory '{local_log_dir}': {e}")
            raise

        return os.path.join(local_log_dir, "backtranslate.log")

    # Removed cycle_counter_filepath property as cycle counting is now in-memory in log_single_file
    # Removed local_log_dir_path property, log_filepath handles directory creation