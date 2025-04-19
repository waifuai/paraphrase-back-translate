"""
Handles back-translation paraphrasing of multiple files using the Gemini API.
"""

import logging
import translate_single_file
import log_single_file
from config import Config, TypeOfTranslation # Import Config and Enum

# Configure logging for this module
logger = logging.getLogger(__name__)

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
    logger.info(f"Starting cycle for translation type: {current_translation_type.name}")
    try:
        # Pass config and current type to translate_single_file
        translate_single_file.translate_single_file(
            config=config,
            current_translation_type=current_translation_type,
        )
        logger.info(f"Translation step completed for {current_translation_type.name}.")

        # Pass config to log_single_cycle
        log_single_file.log_single_cycle(config=config)
        # Logging of cycle completion is handled within log_single_cycle

    except RuntimeError as e:
        # Catch errors like "No files found in directory" from translate_single_file
        logger.error(f"Runtime error during cycle {current_translation_type.name}: {e}. Stopping cycle.")
        # Depending on desired behavior, you might want to stop all cycles here
        # by re-raising the error or setting a flag. For now, just log and stop this cycle.
    except Exception as e:
        logger.exception(f"Unexpected error during cycle {current_translation_type.name}: {e}")
        # Log the full traceback for unexpected errors


def translate_and_log_multi_file(config: Config) -> None:
    """
    Performs multiple back-translation cycles based on the provided configuration.

    Args:
        config: Configuration object containing all parameters.
    """
    current_translation_type = config.initial_translation_type
    logger.info(f"Starting multi-file translation for {config.cycles} cycles. Initial type: {current_translation_type.name}")

    for i in range(config.cycles):
        cycle_num = i + 1
        logger.info(f"--- Beginning Cycle {cycle_num} of {config.cycles} ---")
        try:
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
        except Exception as e:
             logger.error(f"An error occurred in cycle {cycle_num} ({current_translation_type.name}), stopping further cycles. Error: {e}")
             break # Stop processing further cycles if one fails critically

    logger.info("Finished all requested back-translation cycles.")
