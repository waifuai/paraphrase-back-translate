# tests/test_back_translate.py
import unittest
from unittest.mock import patch
import back_translate
import utils

class TestBackTranslate(unittest.TestCase):
    @patch('back_translate.translate_and_log_multi_file.translate_and_log_multi_file')
    def test_main(self, mock_translate_and_log):
        back_translate.main(
            n_cycles=2,
            translation_type="en_to_fr",
            pooling_dir="pool",
            model_dir="model",
            log_dir="log",
        )
        mock_translate_and_log.assert_called_once_with(
            n_cycles=2,
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )

        # Test fr_to_en
        mock_translate_and_log.reset_mock()
        back_translate.main(
            n_cycles=3,
            translation_type="fr_to_en",
            pooling_dir="pool2",
            model_dir="model2",
            log_dir="log2",
        )
        mock_translate_and_log.assert_called_once_with(
            n_cycles=3,
            translation_type=utils.TypeOfTranslation.fr_to_en,
            pooling_dir="pool2",
            model_dir="model2",
            log_dir_stem="log2",
            local_base_dir=".",
        )