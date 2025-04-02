"""
Translates a single file using a specified Hugging Face translation model.
"""

import os
import shutil
import utils # Keep for get_random_file_from_dir
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from config import Config, TypeOfTranslation # Import Config and Enum

# Determine device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

def translate_single_file(
    config: Config,
    current_translation_type: TypeOfTranslation,
) -> None:
    """
    Translates a single file based on the provided configuration and cycle type
    using Hugging Face Transformers.

    Args:
        config: The configuration object.
        current_translation_type: The direction for this specific cycle.
    """
    # --- Main Logic ---
    input_filename = _get_input_file(config, current_translation_type)
    input_filepath = os.path.join(config.get_input_dir(current_translation_type), input_filename)

    # Load model and tokenizer
    model, tokenizer = _load_hf_model_and_tokenizer(config, current_translation_type)

    # Translate file directly from input pool to output pool
    _translate_file(config, model, tokenizer, input_filepath, input_filename, current_translation_type)

    # Move the original input file to completed directory
    _move_input_to_completed(config, current_translation_type, input_filename)


def _get_input_file(config: Config, current_translation_type: TypeOfTranslation) -> str:
    """Returns the filename of a random input file based on the translation type."""
    input_dir = config.get_input_dir(current_translation_type)
    # Returns just the filename, not the full path
    return utils.get_random_file_from_dir(input_dir)


# Removed _copy_input_file_to_local
# Removed _is_model_present


def _load_hf_model_and_tokenizer(config: Config, current_translation_type: TypeOfTranslation):
    """
    Loads the Hugging Face translation model and tokenizer based on config.
    Moves the model to the appropriate device (GPU if available).
    """
    # Removed dummy model logic
    model_name = config.get_hf_model_name(current_translation_type)
    print(f"Loading model and tokenizer: {model_name}")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.to(DEVICE) # Move model to GPU if available
        print(f"Model {model_name} loaded successfully on {DEVICE}.")
        return model, tokenizer
    except OSError as e:
        print(f"Error loading model {model_name}. Check model name and internet connection.")
        raise e


def _translate_file(
    config: Config,
    model,
    tokenizer,
    input_filepath: str,
    input_filename: str, # Needed for output filename
    current_translation_type: TypeOfTranslation
) -> None:
    """
    Performs the translation using the loaded Hugging Face model and tokenizer.
    Reads directly from the input file path and writes directly to the final output path.

    Args:
        config: The configuration object.
        model: The loaded Hugging Face model.
        tokenizer: The loaded Hugging Face tokenizer.
        input_filepath: Full path to the input file in the source pool.
        input_filename: Original filename (used for output).
        current_translation_type: The direction for this cycle.
    """
    print(f"Translating file: {input_filepath}")
    try:
        with open(input_filepath, "r", encoding='utf-8') as f: # Specify encoding
             input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        # Or raise the error depending on desired behavior
        raise

    if not input_text.strip():
        print("Input file is empty or contains only whitespace. Skipping translation.")
        translation = ""
    else:
        try:
            # Tokenize
            inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE) # Move inputs to device

            # Generate translation
            # Adjust generation parameters as needed (e.g., max_length, num_beams)
            translated_tokens = model.generate(**inputs, max_length=512)

            # Decode
            translation = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            print(f"Translation successful.")

        except Exception as e:
            print(f"Error during translation of {input_filename}: {e}")
            # Decide how to handle translation errors (e.g., write empty file, skip, raise)
            translation = f"TRANSLATION_ERROR: {e}" # Example: Write error message

    # Determine final output path
    output_dir_path = config.get_output_dir(current_translation_type)
    final_translated_path = os.path.join(output_dir_path, input_filename) # Output uses original filename

    # Ensure output directory exists
    os.makedirs(output_dir_path, exist_ok=True)

    # Write the translation directly to the final output file
    print(f"Writing translated output to: {final_translated_path}")
    with open(final_translated_path, "w", encoding='utf-8') as f: # Specify encoding
         f.write(translation)
    # No return value needed as file is written directly


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
        print(f"Moving {original_input_path} to {completed_input_path}")
        try:
            shutil.move(original_input_path, completed_input_path)
        except Exception as e:
            print(f"Error moving file {original_input_path} to {completed_input_path}: {e}")
            # Decide how to handle move errors
    else:
        print(f"Warning: Original input file {original_input_path} not found for moving.")

    # Removed logic for moving local translated file and cleaning up local input copy
