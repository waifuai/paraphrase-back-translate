"""
Configuration management for the back-translation project.
"""

import os
from dataclasses import dataclass, field
from enum import Enum

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
    # model_dir: str # Removed - Using HF model names directly
    log_dir: str
    local_base_dir: str = "." # Keep local base dir for now, might simplify later

    # --- Derived properties ---
    # use_dummy_model: bool = field(init=False) # Removed - No dummy model logic
    initial_translation_type: TypeOfTranslation = field(init=False)

    def __post_init__(self):
        """Calculate derived properties after initialization."""
        # self.use_dummy_model = self.model_dir.lower() == "dummy" # Removed
        if self.initial_translation_type_str == "en_to_fr":
            self.initial_translation_type = TypeOfTranslation.en_to_fr
        elif self.initial_translation_type_str == "fr_to_en":
            self.initial_translation_type = TypeOfTranslation.fr_to_en
        else:
            # This should ideally be caught by argparse choices, but good to have defense
            raise ValueError(f"Invalid translation_type: {self.initial_translation_type_str}")

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

    # --- HF Model Name Method ---
    def get_hf_model_name(self, translation_type: TypeOfTranslation) -> str:
        """Returns the Hugging Face model identifier for the given translation type."""
        if translation_type == TypeOfTranslation.en_to_fr:
            return "Helsinki-NLP/opus-mt-en-fr"
        else: # fr_to_en
            return "Helsinki-NLP/opus-mt-fr-en"

    # Removed get_model_filename, get_model_filepath, get_vocab_filename, get_vocab_filepath

    @property
    def cycle_counter_filepath(self) -> str:
        """Returns the absolute path to the cycle counter file."""
        # Uses local_base_dir for log path construction as before
        local_log_dir = os.path.join(self.local_base_dir, self.log_dir)
        # Ensure log directory exists before returning path
        os.makedirs(local_log_dir, exist_ok=True)
        return os.path.join(local_log_dir, "cycle_count.txt")

    @property
    def local_log_dir_path(self) -> str:
        """Returns the absolute path to the local log directory."""
        path = os.path.join(self.local_base_dir, self.log_dir)
        # Ensure log directory exists before returning path
        os.makedirs(path, exist_ok=True)
        return path