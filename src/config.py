"""
Configuration management for the back-translation project using Gemini API.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

class TypeOfTranslation(Enum):
    """Represents the direction of translation."""
    en_to_fr = 1
    fr_to_en = 2

@dataclass
class Config:
    """Holds all configuration parameters for the back-translation process."""
    cycles: int
    initial_translation_type_str: str # "en_to_fr" or "fr_to_en"
    pooling_dir: str
    log_dir: str
    local_base_dir: str = "."
    gemini_model_name: str = "gemini-2.5-pro" # Default Gemini model, updated name
    api_key_path: str = "~/.api-gemini" # Path to the API key file

    # --- Derived properties ---
    initial_translation_type: TypeOfTranslation = field(init=False)
    api_key: str = field(init=False)

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

        # Load API Key
        self._load_api_key()

    def _load_api_key(self):
        """Loads the Gemini API key from the specified file path."""
        expanded_path = os.path.expanduser(self.api_key_path)
        logger.info(f"Attempting to load Gemini API key from: {expanded_path}")
        try:
            with open(expanded_path, "r", encoding='utf-8') as f:
                self.api_key = f.read().strip()
            if not self.api_key:
                raise ValueError("API key file is empty.")
            logger.info("Gemini API key loaded successfully.")
        except FileNotFoundError:
            logger.error(f"Error: API key file not found at {expanded_path}")
            raise FileNotFoundError(f"API key file not found at {expanded_path}. Please create it and add your key.")
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