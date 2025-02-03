"""
Handles back-translation paraphrasing of multiple files.
"""

import utils
import translate_single_file
import log_single_file

def translate_and_log_single_cycle(
    translation_type: utils.TypeOfTranslation,
    pooling_dir: str,
    model_dir: str,
    log_dir_stem: str,
    local_base_dir: str,
) -> None:
    """
    Performs a single back-translation cycle (translation and logging).
    """
    translate_single_file.translate_single_file(
        translation_type=translation_type,
        pooling_dir=pooling_dir,
        model_dir=model_dir,
    )

    log_single_file.log_single_cycle(
        log_dir_stem=log_dir_stem,
        local_base_dir=local_base_dir,
    )

def translate_and_log_multi_file(
    n_cycles: int,
    translation_type: utils.TypeOfTranslation,
    pooling_dir: str,
    model_dir: str,
    log_dir_stem: str,
    local_base_dir: str,
) -> None:
    """
    Performs multiple back-translation cycles.

    Args:
        n_cycles: Number of cycles to perform.
        translation_type: Initial translation direction.
        pooling_dir: Directory containing input/output files.
        model_dir: Directory containing the translation model and vocab files.
        log_dir_stem: Base name for the log directory.
        local_base_dir: Base directory (local only).
    """
    for _ in range(n_cycles):
        translate_and_log_single_cycle(
            translation_type=translation_type,
            pooling_dir=pooling_dir,
            model_dir=model_dir,
            log_dir_stem=log_dir_stem,
            local_base_dir=local_base_dir,
        )
        # Reverse translation direction for the next cycle.
        translation_type = (
            utils.TypeOfTranslation.fr_to_en
            if translation_type == utils.TypeOfTranslation.en_to_fr
            else utils.TypeOfTranslation.en_to_fr
        )
