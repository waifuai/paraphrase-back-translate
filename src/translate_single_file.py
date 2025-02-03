"""
Translates a single file using a specified translation model via Trax.
"""

import os
import shutil
import utils
import trax
import trax.data
import trax.supervised.decoding

def translate_single_file(
    translation_type: utils.TypeOfTranslation,
    pooling_dir: str,
    model_dir: str,
) -> None:
    """
    Translates a single file.

    Args:
        translation_type: The direction of translation.
        pooling_dir: The directory containing input/output files.
        model_dir: The directory containing the translation model and vocabulary files.
                   For testing, use "dummy" to trigger a dummy translator.
    """
    input_file = _get_input_file(translation_type, pooling_dir)
    _copy_input_file_to_local(input_file, translation_type, pooling_dir)

    if model_dir.lower() != "dummy" and not _is_model_present(model_dir, translation_type):
        raise FileNotFoundError(f"Model file not found in {model_dir}")

    model = _load_model(model_dir, translation_type)
    translated_file = _translate_file(model, input_file, translation_type, model_dir)
    _move_files(translation_type, input_file, translated_file, pooling_dir)

def _get_input_file(translation_type: utils.TypeOfTranslation, pooling_dir: str) -> str:
    """Returns a random input file based on the translation type."""
    pool = "input_pool" if translation_type == utils.TypeOfTranslation.en_to_fr else "french_pool"
    input_dir = os.path.join(pooling_dir, pool)
    return utils.get_random_file_from_dir(input_dir)

def _copy_input_file_to_local(input_file: str, translation_type: utils.TypeOfTranslation, pooling_dir: str) -> None:
    """Copies the selected input file to the local directory."""
    pool = "input_pool" if translation_type == utils.TypeOfTranslation.en_to_fr else "french_pool"
    source_path = os.path.join(pooling_dir, pool, input_file)
    shutil.copy(source_path, ".")
    print(f"Copied input file: {input_file}")

def _is_model_present(model_dir: str, translation_type: utils.TypeOfTranslation) -> bool:
    """Checks if the expected model file exists."""
    filename = "model_en_fr.pkl.gz" if translation_type == utils.TypeOfTranslation.en_to_fr else "model_fr_en.pkl.gz"
    model_file = os.path.join(model_dir, filename)
    return os.path.exists(model_file)

def _load_model(model_dir: str, translation_type: utils.TypeOfTranslation):
    """
    Loads the translation model using Trax.
    For testing, if model_dir is "dummy", returns a dummy translator.
    """
    if model_dir.lower() == "dummy":
        # Dummy translator: simply reverses the text.
        return lambda text: text[::-1]
    filename = "model_en_fr.pkl.gz" if translation_type == utils.TypeOfTranslation.en_to_fr else "model_fr_en.pkl.gz"
    model_file = os.path.join(model_dir, filename)
    model = trax.models.Transformer(
       input_vocab_size=33300,
       d_model=512, d_ff=2048,
       n_heads=8, n_encoder_layers=6, n_decoder_layers=6,
       max_len=2048, mode='predict')
    model.init_from_file(model_file, weights_only=True)
    return model

def _get_vocab_params(translation_type: utils.TypeOfTranslation, model_dir: str):
    """
    Returns the local vocabulary directory and file name based on translation direction.
    Assumes that the vocabulary files (e.g. 'vocab_en_fr.subword') reside in model_dir.
    """
    if translation_type == utils.TypeOfTranslation.en_to_fr:
         return model_dir, "vocab_en_fr.subword"
    else:
         return model_dir, "vocab_fr_en.subword"

def _translate_file(model, input_file: str, translation_type: utils.TypeOfTranslation, model_dir: str) -> str:
    """
    Performs the translation using Trax if a real model is loaded,
    or uses the dummy function if in test mode.
    """
    with open(input_file, "r") as f:
         input_text = f.read()

    # If model is a Trax model (assumed to have an 'apply' attribute), use the Trax pipeline.
    if hasattr(model, "apply"):
         vocab_dir, vocab_file = _get_vocab_params(translation_type, model_dir)
         tokenized = list(trax.data.tokenize(iter([input_text]), vocab_dir=vocab_dir, vocab_file=vocab_file))[0]
         tokenized = tokenized[None, :]  # Add batch dimension.
         tokenized_translation = trax.supervised.decoding.autoregressive_sample(model, tokenized, temperature=0.0)
         tokenized_translation = tokenized_translation[0][:-1]  # Remove EOS token.
         translation = trax.data.detokenize(tokenized_translation, vocab_dir=vocab_dir, vocab_file=vocab_file)
    else:
         # Dummy translation.
         translation = model(input_text)

    translated_file = input_file + ".translated"
    with open(translated_file, "w") as f:
         f.write(translation)
    return translated_file

def _move_files(
    translation_type: utils.TypeOfTranslation,
    input_file: str,
    translated_file: str,
    pooling_dir: str,
) -> None:
    """Moves input and translated files to appropriate directories."""
    source_dir = "input_pool" if translation_type == utils.TypeOfTranslation.en_to_fr else "french_pool"
    completed_dir = f"{source_dir}_completed"
    translated_dir = "french_pool" if translation_type == utils.TypeOfTranslation.en_to_fr else "output_pool"

    os.makedirs(os.path.join(pooling_dir, completed_dir), exist_ok=True)
    shutil.move(os.path.join(pooling_dir, source_dir, input_file), os.path.join(pooling_dir, completed_dir))
    os.makedirs(os.path.join(pooling_dir, translated_dir), exist_ok=True)
    shutil.move(translated_file, os.path.join(pooling_dir, translated_dir, input_file))
