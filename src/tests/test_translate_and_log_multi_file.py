# tests/test_translate_and_log_multi_file.py
import unittest
from unittest.mock import patch
import translate_and_log_multi_file as talmf
from config import Config, TypeOfTranslation # Import Config and Enum
# import utils # No longer needed here

class TestTranslateAndLogMultiFile(unittest.TestCase):
    @patch('translate_and_log_multi_file.log_single_file.log_single_cycle')
    @patch('translate_and_log_multi_file.translate_single_file.translate_single_file')
    def test_translate_and_log_single_cycle(self, mock_translate, mock_log):
        # Create a dummy config
        test_config = Config(
            cycles=1, # Not used by single cycle func
            initial_translation_type_str="en_to_fr", # Not used directly here
            pooling_dir="pool",
            model_dir="model",
            log_dir="log",
        )
        current_type = TypeOfTranslation.en_to_fr

        # Call the function with config and current type
        talmf.translate_and_log_single_cycle(
            config=test_config,
            current_translation_type=current_type,
        )

        # Check that translate_single_file was called correctly
        mock_translate.assert_called_once_with(
            config=test_config,
            current_translation_type=current_type,
        )
        # Check that log_single_cycle was called correctly
        mock_log.assert_called_once_with(config=test_config)


    @patch('translate_and_log_multi_file.translate_and_log_single_cycle')
    def test_translate_and_log_multi_file(self, mock_single_cycle):
        # Create a config for 2 cycles, starting en_to_fr
        test_config_2_cycles = Config(
            cycles=2,
            initial_translation_type_str="en_to_fr",
            pooling_dir="pool",
            model_dir="model",
            log_dir="log",
        )

        # Call the function with the config object
        talmf.translate_and_log_multi_file(config=test_config_2_cycles)

        # Assert it was called twice
        self.assertEqual(mock_single_cycle.call_count, 2)
        # Check first call (en_to_fr)
        mock_single_cycle.assert_any_call(
            config=test_config_2_cycles,
            current_translation_type=TypeOfTranslation.en_to_fr,
        )
        # Check second call (fr_to_en)
        mock_single_cycle.assert_any_call(
            config=test_config_2_cycles,
            current_translation_type=TypeOfTranslation.fr_to_en,
        )

        # --- Test with n_cycles = 0 ---
        mock_single_cycle.reset_mock()
        test_config_0_cycles = Config(
            cycles=0,
            initial_translation_type_str="en_to_fr",
            pooling_dir="pool",
            model_dir="model",
            log_dir="log",
        )
        talmf.translate_and_log_multi_file(config=test_config_0_cycles)
        mock_single_cycle.assert_not_called()  # Should not be called with 0 cycles