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
    model_dir: str
    log_dir: str
    local_base_dir: str = "." # Keep local base dir for now, might simplify later

    # --- Derived properties ---
    use_dummy_model: bool = field(init=False)
    initial_translation_type: TypeOfTranslation = field(init=False)

    def __post_init__(self):
        """Calculate derived properties after initialization."""
        self.use_dummy_model = self.model_dir.lower() == "dummy"
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

    def get_model_filename(self, translation_type: TypeOfTranslation) -> str:
        """Returns the expected model filename for the given translation type."""
        return "model_en_fr.pkl.gz" if translation_type == TypeOfTranslation.en_to_fr else "model_fr_en.pkl.gz"

    def get_model_filepath(self, translation_type: TypeOfTranslation) -> str:
        """Returns the absolute path to the model file."""
        # Returns dummy path if using dummy model, otherwise constructs path
        return "" if self.use_dummy_model else os.path.join(self.model_dir, self.get_model_filename(translation_type))

    def get_vocab_filename(self, translation_type: TypeOfTranslation) -> str:
        """Returns the expected vocabulary filename for the given translation type."""
        return "vocab_en_fr.subword" if translation_type == TypeOfTranslation.en_to_fr else "vocab_fr_en.subword"

    def get_vocab_filepath(self, translation_type: TypeOfTranslation) -> str:
        """Returns the absolute path to the vocabulary file."""
         # Returns dummy path if using dummy model, otherwise constructs path
        return "" if self.use_dummy_model else os.path.join(self.model_dir, self.get_vocab_filename(translation_type))

    @property
    def cycle_counter_filepath(self) -> str:
        """Returns the absolute path to the cycle counter file."""
        # Uses local_base_dir for log path construction as before
        local_log_dir = os.path.join(self.local_base_dir, self.log_dir)
        return os.path.join(local_log_dir, "cycle_count.txt")

    @property
    def local_log_dir_path(self) -> str:
        """Returns the absolute path to the local log directory."""
        return os.path.join(self.local_base_dir, self.log_dir)