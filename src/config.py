"""
Configuration management for the back-translation project using Gemini API.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

# Configure logging for this module
logger = logging.getLogger(__name__)

class TypeOfTranslation(Enum):
    """Represents the direction of translation."""
    en_to_fr = 1
    fr_to_en = 2

DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
DEFAULT_OPENROUTER_MODEL = "openrouter/horizon-beta"

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
    initial_translation_type_str: str # "en_to_fr" or "fr_to_en"
    pooling_dir: str
    log_dir: str
    local_base_dir: str = "."
    # Back-compat: gemini specific override if no common model provided and provider == gemini
    gemini_model_name: str = DEFAULT_GEMINI_MODEL
    api_key_path: str = "~/.api-gemini" # Path to the API key file for Gemini
    # New provider and model fields
    provider: Provider = Provider.openrouter  # Default provider switched to OpenRouter
    model_name: str | None = None            # Common model override (applies to any provider)

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
        """
        # 1) Explicit override takes precedence
        if self.model_name and str(self.model_name).strip():
            return str(self.model_name).strip()

        # 2) Provider-specific model files
        try:
            if self.provider == Provider.openrouter:
                if MODEL_FILE_OPENROUTER.is_file():
                    content = MODEL_FILE_OPENROUTER.read_text(encoding="utf-8").strip()
                    if content:
                        return content
            elif self.provider == Provider.gemini:
                if MODEL_FILE_GEMINI.is_file():
                    content = MODEL_FILE_GEMINI.read_text(encoding="utf-8").strip()
                    if content:
                        return content
        except Exception as e:
            # Non-fatal; fall through to defaults
            logger.debug(f"Failed to read provider model file: {e}")

        # 3) Back-compat for Gemini: prefer gemini_model_name if provider is gemini
        if self.provider == Provider.gemini and (self.gemini_model_name and self.gemini_model_name.strip()):
            return self.gemini_model_name.strip()

        # 4) Provider-specific defaults
        return DEFAULT_OPENROUTER_MODEL if self.provider == Provider.openrouter else DEFAULT_GEMINI_MODEL

    def _load_api_key(self):
        """
        Loads the Gemini API key with the following precedence:
        1) Environment variable GEMINI_API_KEY
        2) Environment variable GOOGLE_API_KEY
        3) Fallback: contents of the file at api_key_path (default ~/.api-gemini)
        """
        env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_key and env_key.strip():
            self.api_key = env_key.strip()
            logger.info("Gemini API key loaded from environment variable.")
            return

        expanded_path = os.path.expanduser(self.api_key_path)
        logger.info(f"Attempting to load Gemini API key from: {expanded_path}")
        try:
            with open(expanded_path, "r", encoding='utf-8') as f:
                self.api_key = f.read().strip()
            if not self.api_key:
                raise ValueError("API key file is empty.")
            logger.info("Gemini API key loaded successfully from file.")
        except FileNotFoundError:
            logger.error(f"Error: API key not found in environment and file not found at {expanded_path}")
            raise FileNotFoundError(
                f"API key not found in environment and file not found at {expanded_path}. "
                "Set GEMINI_API_KEY or GOOGLE_API_KEY, or create the key file."
            )
        except Exception as e:
            logger.error(f"Error reading API key file {expanded_path}: {e}")
            raise e

    # --- Path generation methods ---

    def _get_pool_name(self, translation_type: TypeOfTranslation) -> str:
        """Helper to get the base pool name for a given direction."""
        return "input_pool" if translation_type == TypeOfTranslation.en_to_fr else "french_pool"

    def get_input_dir(self, translation_type: TypeOfTranslation) -> str:
        """Returns the absolute path to the input directory for the given translation type."""
        return os.path.join(self.pooling_dir, self._get_pool_name(translation_type))

    def get_output_dir(self, translation_type: TypeOfTranslation) -> str:
        """Returns the absolute path to the output directory for the given translation type."""
        output_pool = "french_pool" if translation_type == TypeOfTranslation.en_to_fr else "output_pool"
        return os.path.join(self.pooling_dir, output_pool)

    def get_completed_dir(self, translation_type: TypeOfTranslation) -> str:
        """Returns the absolute path to the completed directory for the given translation type."""
        completed_pool = f"{self._get_pool_name(translation_type)}_completed"
        return os.path.join(self.pooling_dir, completed_pool)

    @property
    def log_filepath(self) -> str:
        """Returns the absolute path to the log file."""
        # Uses local_base_dir for log path construction
        local_log_dir = os.path.join(self.local_base_dir, self.log_dir)
        # Ensure log directory exists before returning path
        os.makedirs(local_log_dir, exist_ok=True)
        return os.path.join(local_log_dir, "backtranslate.log")

    # Removed cycle_counter_filepath property as cycle counting is now in-memory in log_single_file
    # Removed local_log_dir_path property, log_filepath handles directory creation