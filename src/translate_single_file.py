"""
Translates a single file using the specified Gemini API model.
"""

import os
import shutil
import logging
from google import genai
import utils # Keep for get_random_file_from_dir
from config import Config, TypeOfTranslation, DEFAULT_GEMINI_MODEL # Import Config and Enum

# Configure logging for this module
logger = logging.getLogger(__name__)

# --- Gemini Client Configuration ---
# Client is configured dynamically within _translate_file using the API key from Config

def translate_single_file(
    config: Config,
    current_translation_type: TypeOfTranslation,
) -> None:
    """
    Translates a single file based on the provided configuration and cycle type
    using the Gemini API.

    Args:
        config: The configuration object, containing API key and model name.
        current_translation_type: The direction for this specific cycle.
    """
    # --- Main Logic ---
    input_filename = _get_input_file(config, current_translation_type)
    input_filepath = os.path.join(config.get_input_dir(current_translation_type), input_filename)

    # Translate file directly from input pool to output pool using Gemini
    _translate_file_with_gemini(config, input_filepath, input_filename, current_translation_type)

    # Move the original input file to completed directory
    _move_input_to_completed(config, current_translation_type, input_filename)


def _get_input_file(config: Config, current_translation_type: TypeOfTranslation) -> str:
    """Returns the filename of a random input file based on the translation type."""
    input_dir = config.get_input_dir(current_translation_type)
    logger.info(f"Looking for input file in: {input_dir}")
    try:
        filename = utils.get_random_file_from_dir(input_dir)
        logger.info(f"Selected input file: {filename}")
        return filename
    except RuntimeError as e:
        logger.error(f"Error getting input file: {e}")
        raise # Re-raise the error to stop the process if no input file found


def _translate_file_with_gemini(
    config: Config,
    input_filepath: str,
    input_filename: str, # Needed for output filename
    current_translation_type: TypeOfTranslation
) -> None:
    """
    Performs the translation using the Gemini API.
    Reads directly from the input file path and writes directly to the final output path.

    Args:
        config: The configuration object (contains API key, model name).
        input_filepath: Full path to the input file in the source pool.
        input_filename: Original filename (used for output).
        current_translation_type: The direction for this cycle.
    """
    logger.info(f"Translating file using Gemini: {input_filepath}")

    # 1. Configure Google GenAI Client
    try:
        client = genai.Client(api_key=config.api_key)
        model_name = config.gemini_model_name or DEFAULT_GEMINI_MODEL
        logger.info(f"GenAI client initialized with model: {model_name}")
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        _write_translation_output(config, input_filename, current_translation_type, f"GEMINI_CONFIG_ERROR: {e}")
        return

    # 2. Read Input Text
    try:
        with open(input_filepath, "r", encoding='utf-8') as f:
             input_text = f.read()
        if not input_text.strip():
            logger.warning(f"Input file {input_filename} is empty or contains only whitespace. Skipping translation.")
            translation = "" # Write empty file for empty input
            _write_translation_output(config, input_filename, current_translation_type, translation)
            return
    except FileNotFoundError:
        logger.error(f"Input file not found at {input_filepath} during translation attempt.")
        _write_translation_output(config, input_filename, current_translation_type, f"FILE_NOT_FOUND_ERROR: {input_filepath}")
        return
    except Exception as e:
        logger.error(f"Error reading input file {input_filepath}: {e}")
        _write_translation_output(config, input_filename, current_translation_type, f"FILE_READ_ERROR: {e}")
        return

    # 3. Construct Prompt
    source_lang = "English" if current_translation_type == TypeOfTranslation.en_to_fr else "French"
    target_lang = "French" if current_translation_type == TypeOfTranslation.en_to_fr else "English"
    prompt = f"Translate the following {source_lang} text to {target_lang}:\n\n{input_text}"

    # 4. Call Gemini API via google-genai SDK
    translation = ""
    try:
        logger.info(f"Sending request to Gemini API for file: {input_filename}")
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        # The new SDK returns text on response.output_text
        if hasattr(response, "output_text") and response.output_text:
            translation = response.output_text
            logger.info(f"Translation successful for file: {input_filename}")
        else:
            # Fallback attempts for robustness across SDK minor versions
            text_candidate = getattr(response, "text", "") or getattr(response, "candidates", "")
            if text_candidate:
                translation = str(text_candidate)
                logger.info(f"Translation extracted via fallback field for file: {input_filename}")
            else:
                logger.warning(f"GenAI response for {input_filename} was empty or blocked. Raw response present but no text.")
                translation = "GEMINI_RESPONSE_EMPTY_OR_BLOCKED"
    except Exception as e:
        logger.error(f"Error during GenAI API call for {input_filename}: {e}")
        translation = f"GEMINI_API_ERROR: {e}"

    # 5. Write Output
    _write_translation_output(config, input_filename, current_translation_type, translation)


def _write_translation_output(
    config: Config,
    input_filename: str,
    current_translation_type: TypeOfTranslation,
    translation: str
) -> None:
    """Helper function to write the translation (or error message) to the output file."""
    output_dir_path = config.get_output_dir(current_translation_type)
    final_translated_path = os.path.join(output_dir_path, input_filename) # Output uses original filename

    # Ensure output directory exists
    os.makedirs(output_dir_path, exist_ok=True)

    # Write the translation/error directly to the final output file
    logger.info(f"Writing output to: {final_translated_path}")
    try:
        with open(final_translated_path, "w", encoding='utf-8') as f:
             f.write(translation)
    except Exception as e:
        logger.error(f"Error writing output file {final_translated_path}: {e}")
        # Log the error, but the process might continue with the next file


def _move_input_to_completed(
    config: Config,
    current_translation_type: TypeOfTranslation,
    input_filename: str # Original filename from the pool
) -> None:
    """
    Moves the original input file to the completed directory, using paths from config.
    """
    # Get directories from config
    source_dir_path = config.get_input_dir(current_translation_type)
    completed_dir_path = config.get_completed_dir(current_translation_type)

    # Define source and destination paths
    original_input_path = os.path.join(source_dir_path, input_filename)
    completed_input_path = os.path.join(completed_dir_path, input_filename)

    # Ensure completed directory exists
    os.makedirs(completed_dir_path, exist_ok=True)

    # Move original input file to completed
    if os.path.exists(original_input_path):
        logger.info(f"Moving {original_input_path} to {completed_input_path}")
        try:
            shutil.move(original_input_path, completed_input_path)
        except Exception as e:
            logger.error(f"Error moving file {original_input_path} to {completed_input_path}: {e}")
            # Log the error, but allow the cycle to potentially continue
    else:
        logger.warning(f"Original input file {original_input_path} not found for moving (might have been processed already or deleted).")
