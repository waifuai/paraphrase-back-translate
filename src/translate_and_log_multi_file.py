"""
Handles back-translation paraphrasing of multiple files.
"""

# import utils # No longer needed directly here
import translate_single_file
import log_single_file
from config import Config, TypeOfTranslation # Import Config and Enum

def translate_and_log_single_cycle(
    config: Config,
    current_translation_type: TypeOfTranslation,
) -> None:
    """
    Performs a single back-translation cycle (translation and logging).

    Args:
        config: The configuration object.
        current_translation_type: The direction for this specific cycle.
    """
    # Pass config and current type to translate_single_file
    translate_single_file.translate_single_file(
        config=config,
        current_translation_type=current_translation_type,
    )

    # Pass config to log_single_cycle (it contains log_dir and local_base_dir)
    log_single_file.log_single_cycle(config=config)


def translate_and_log_multi_file(config: Config) -> None:
    """
    Performs multiple back-translation cycles based on the provided configuration.

    Args:
        config: Configuration object containing all parameters.
    """
    current_translation_type = config.initial_translation_type

    for _ in range(config.cycles):
        translate_and_log_single_cycle(
            config=config,
            current_translation_type=current_translation_type,
        )
        # Reverse translation direction for the next cycle.
        current_translation_type = (
            TypeOfTranslation.fr_to_en
            if current_translation_type == TypeOfTranslation.en_to_fr
            else TypeOfTranslation.en_to_fr
        )
