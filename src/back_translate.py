"""
Main entry point for back-translation paraphrasing.
"""

import translate_and_log_multi_file
import utils

def main(n_cycles: int, translation_type: str, pooling_dir: str, model_dir: str, log_dir: str):
    """
    Main entry point for the program.

    Args:
        n_cycles: Number of back-translation cycles.
        translation_type: Either "en_to_fr" or "fr_to_en".
        pooling_dir: Directory with input/output files.
        model_dir: Directory for the translation model and vocabulary files.
        log_dir: Directory for logs.
    """
    # Convert string to enum.
    if translation_type == "en_to_fr":
        trans_enum = utils.TypeOfTranslation.en_to_fr
    else:
        trans_enum = utils.TypeOfTranslation.fr_to_en

    # Run locally (no remote directories).
    local_base_dir = "."

    translate_and_log_multi_file.translate_and_log_multi_file(
        n_cycles=n_cycles,
        translation_type=trans_enum,
        pooling_dir=pooling_dir,
        model_dir=model_dir,
        log_dir_stem=log_dir,
        local_base_dir=local_base_dir,
    )

if __name__ == "__main__":
    # Default parameters if run directly.
    main(
        n_cycles=1,
        translation_type="en_to_fr",
        pooling_dir="./data/pooling",
        model_dir="./models",
        log_dir="./logs",
    )
