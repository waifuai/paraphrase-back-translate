# tests/test_main.py
import unittest
from unittest.mock import patch
import main

class TestMain(unittest.TestCase):

    @patch('main.main')  # Mock the main function from back_translate
    def test_main_cli(self, mock_main):
        # Simulate command-line arguments.
        test_args = [
            "main.py",  # Program name (not used by argparse)
            "--cycles", "3",
            "--translation-type", "fr_to_en",
            "--pooling-dir", "test_pool",
            "--model-dir", "test_model",
            "--log-dir", "test_log"
        ]

        with patch('sys.argv', test_args):
            main.main_cli()

        mock_main.assert_called_once_with(
            n_cycles=3,
            translation_type="fr_to_en",
            pooling_dir="test_pool",
            model_dir="test_model",
            log_dir="test_log"
        )

        # test default arguments
        mock_main.reset_mock()
        test_args = ["main.py"]  # Use default
        with patch('sys.argv', test_args):
             main.main_cli()
        mock_main.assert_called_once_with(
             n_cycles=1,
             translation_type="en_to_fr",
             pooling_dir="./data/pooling",
             model_dir="./models",
             log_dir="./logs"
         )