# tests/test_translate_and_log_multi_file.py
import unittest
from unittest.mock import patch
import translate_and_log_multi_file as talmf
import utils

class TestTranslateAndLogMultiFile(unittest.TestCase):
    @patch('translate_and_log_multi_file.log_single_file.log_single_cycle')
    @patch('translate_and_log_multi_file.translate_single_file.translate_single_file')
    def test_translate_and_log_single_cycle(self, mock_translate, mock_log):
        talmf.translate_and_log_single_cycle(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )
        mock_translate.assert_called_once_with(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
        )
        mock_log.assert_called_once_with(
            log_dir_stem="log",
            local_base_dir=".",
        )

    @patch('translate_and_log_multi_file.translate_and_log_single_cycle')
    def test_translate_and_log_multi_file(self, mock_single_cycle):
        talmf.translate_and_log_multi_file(
            n_cycles=2,
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )
        # en_to_fr then fr_to_en
        self.assertEqual(mock_single_cycle.call_count, 2)
        mock_single_cycle.assert_any_call(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )
        mock_single_cycle.assert_any_call(
            translation_type=utils.TypeOfTranslation.fr_to_en,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )

        # Test with n_cycles = 0.
        mock_single_cycle.reset_mock()
        talmf.translate_and_log_multi_file(
            n_cycles=0,
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir="pool",
            model_dir="model",
            log_dir_stem="log",
            local_base_dir=".",
        )
        mock_single_cycle.assert_not_called()  # Should not be called with 0 cycles