"""
Translates a single file using a specified translation model via Trax.
"""

import os
import shutil
import utils # Keep for get_random_file_from_dir
# Defer trax imports until needed
# import trax
# import trax.data
# import trax.supervised.decoding
from config import Config, TypeOfTranslation # Import Config and Enum

def translate_single_file(
    config: Config,
    current_translation_type: TypeOfTranslation,
) -> None:
    """
    Translates a single file based on the provided configuration and cycle type.

    Args:
        config: The configuration object.
        current_translation_type: The direction for this specific cycle.
    """
    # --- Main Logic (will be updated after helpers) ---
    input_filename = _get_input_file(config, current_translation_type)
    local_input_filepath = _copy_input_file_to_local(config, current_translation_type, input_filename)

    # Check model presence using config
    if not config.use_dummy_model and not _is_model_present(config, current_translation_type):
        raise FileNotFoundError(f"Model file not found in {config.model_dir} for type {current_translation_type}")

    # Load model using config
    model = _load_model(config, current_translation_type)
    # Translate file using config and local path (assuming local path needed for now)
    # Note: input_file variable is no longer used here, using local_input_filepath
    translated_filepath = _translate_file(config, model, local_input_filepath, current_translation_type)
    # Move files using config
    _move_files(config, current_translation_type, input_filename, translated_filepath)


def _get_input_file(config: Config, current_translation_type: TypeOfTranslation) -> str:
    """Returns the filename of a random input file based on the translation type."""
    input_dir = config.get_input_dir(current_translation_type)
    # Returns just the filename, not the full path
    return utils.get_random_file_from_dir(input_dir)


def _copy_input_file_to_local(
    config: Config,
    current_translation_type: TypeOfTranslation,
    input_filename: str
) -> str:
    """
    Copies the selected input file to the local directory (`.`).
    TODO: Investigate if this copy is necessary or if translation can read directly.
          If needed, consider using tempfile module.

    Returns:
        The path to the local copy of the input file (currently just the filename).
    """
    input_dir = config.get_input_dir(current_translation_type)
    source_path = os.path.join(input_dir, input_filename)
    # Copy to current directory for now. The destination path is just the filename.
    local_copy_path = os.path.basename(input_filename) # Or just input_filename if always in root
    shutil.copy(source_path, local_copy_path)
    print(f"Copied input file: {input_filename} to {local_copy_path}")
    return local_copy_path # Return the path to the local copy


def _is_model_present(config: Config, current_translation_type: TypeOfTranslation) -> bool:
    """Checks if the expected model file exists using the config object."""
    # config.get_model_filepath handles the dummy case implicitly (returns "")
    model_filepath = config.get_model_filepath(current_translation_type)
    return os.path.exists(model_filepath)


def _load_model(config: Config, current_translation_type: TypeOfTranslation):
    """
    Loads the translation model using Trax or returns a dummy translator, based on config.
    """
    if config.use_dummy_model:
        # Dummy translator: simply reverses the text.
        print("Using dummy translator.")
        return lambda text: text[::-1]

    # Get model path from config
    model_filepath = config.get_model_filepath(current_translation_type)
    print(f"Loading model from: {model_filepath}")
    import trax # Import trax here

    # Initialize and load the Trax model
    model = trax.models.Transformer(
       input_vocab_size=33300, # TODO: Consider making vocab size configurable?
       d_model=512, d_ff=2048,
       n_heads=8, n_encoder_layers=6, n_decoder_layers=6,
       max_len=2048, mode='predict') # TODO: Make model params configurable?
    model.init_from_file(model_filepath, weights_only=True)
    return model


# This function is no longer strictly needed as config provides the paths directly
# def _get_vocab_params(config: Config, current_translation_type: TypeOfTranslation):
#     """
#     Returns the vocabulary directory and file name based on config.
#     """
#     vocab_filename = config.get_vocab_filename(current_translation_type)
#     # Vocab files are expected in the model_dir
#     return config.model_dir, vocab_filename


def _translate_file(
    config: Config,
    model, # Can be Trax model or dummy lambda
    local_input_filepath: str,
    current_translation_type: TypeOfTranslation
) -> str:
    """
    Performs the translation using the loaded model (Trax or dummy).
    Reads from the local input file path and writes to a local translated file path.

    Args:
        config: The configuration object.
        model: The loaded Trax model or dummy translator function.
        local_input_filepath: Path to the input file copied locally.
        current_translation_type: The direction for this cycle.

    Returns:
        The path to the locally created translated file.
    """
    print(f"Translating file: {local_input_filepath}")
    with open(local_input_filepath, "r") as f:
         input_text = f.read()

         import trax.data
         import trax.supervised.decoding # Import trax here
    # Check if it's a real Trax model (has 'apply') or the dummy lambda
    if not config.use_dummy_model and hasattr(model, "apply"):
         # Use config to get vocab details
         vocab_dir = config.model_dir # Vocab files are in model_dir
         vocab_file = config.get_vocab_filename(current_translation_type)
         print(f"Using vocab: dir='{vocab_dir}', file='{vocab_file}'")

         tokenized = list(trax.data.tokenize(iter([input_text]), vocab_dir=vocab_dir, vocab_file=vocab_file))[0]
         tokenized = tokenized[None, :]  # Add batch dimension.
         tokenized_translation = trax.supervised.decoding.autoregressive_sample(model, tokenized, temperature=0.0) # Use temperature from config?
         tokenized_translation = tokenized_translation[0][:-1]  # Remove EOS token.
         translation = trax.data.detokenize(tokenized_translation, vocab_dir=vocab_dir, vocab_file=vocab_file)
    else:
         # Dummy translation (model is the lambda function)
         print("Applying dummy translation (reversing text).")
         translation = model(input_text)

    # Create the translated file locally (e.g., "input.txt.translated")
    translated_filepath = local_input_filepath + ".translated"
    print(f"Writing translated output to: {translated_filepath}")
    with open(translated_filepath, "w") as f:
         f.write(translation)
    return translated_filepath


def _move_files(
    config: Config,
    current_translation_type: TypeOfTranslation,
    input_filename: str, # Original filename from the pool
    local_translated_filepath: str # Path to the file created by _translate_file
) -> None:
    """
    Moves the original input file to the completed directory and the locally
    translated file to the appropriate output directory, using paths from config.
    """
    # Get directories from config
    source_dir_path = config.get_input_dir(current_translation_type)
    completed_dir_path = config.get_completed_dir(current_translation_type)
    output_dir_path = config.get_output_dir(current_translation_type)

    # Define source and destination paths
    original_input_path = os.path.join(source_dir_path, input_filename)
    completed_input_path = os.path.join(completed_dir_path, input_filename)
    final_translated_path = os.path.join(output_dir_path, input_filename) # Output uses original filename

    # Ensure directories exist
    os.makedirs(completed_dir_path, exist_ok=True)
    os.makedirs(output_dir_path, exist_ok=True)

    # Move original input file to completed
    print(f"Moving {original_input_path} to {completed_input_path}")
    shutil.move(original_input_path, completed_input_path)

    # Move locally translated file to final output directory
    print(f"Moving {local_translated_filepath} to {final_translated_path}")
    shutil.move(local_translated_filepath, final_translated_path)

    # Clean up the local input file copy?
    local_input_filepath = os.path.basename(input_filename) # Path used in _copy_input_file_to_local
    if os.path.exists(local_input_filepath):
        print(f"Removing local input copy: {local_input_filepath}")
        os.remove(local_input_filepath)
