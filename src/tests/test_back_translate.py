# tests/test_back_translate.py
import unittest
from unittest.mock import patch
import back_translate
from config import Config # Import Config
# import utils # No longer needed for TypeOfTranslation

class TestBackTranslate(unittest.TestCase):
    @patch('back_translate.translate_and_log_multi_file.translate_and_log_multi_file')
    def test_main(self, mock_translate_and_log):
        # Create a Config object for the first test case
        config1 = Config(
            cycles=2,
            initial_translation_type_str="en_to_fr",
            pooling_dir="pool",
            # model_dir="model", # Removed
            log_dir="log",
        )
        # Call main with the config object
        back_translate.main(config=config1)

        # Assert that the mock was called once with the config object
        mock_translate_and_log.assert_called_once_with(config=config1)

        # --- Test fr_to_en ---
        mock_translate_and_log.reset_mock()

        # Create a Config object for the second test case
        config2 = Config(
            cycles=3,
            initial_translation_type_str="fr_to_en",
            pooling_dir="pool2",
            # model_dir="model2", # Removed
            log_dir="log2",
        )
        # Call main with the second config object
        back_translate.main(config=config2)

        # Assert that the mock was called once with the second config object
        mock_translate_and_log.assert_called_once_with(config=config2)