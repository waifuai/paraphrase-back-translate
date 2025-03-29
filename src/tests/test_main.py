# tests/test_main.py
import unittest
from unittest.mock import patch
import main
from config import Config, TypeOfTranslation # Import Config

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

        # Assert called once, then check the config object passed
        mock_main.assert_called_once()
        call_args, call_kwargs = mock_main.call_args
        self.assertIn('config', call_kwargs)
        config_arg = call_kwargs['config']
        self.assertIsInstance(config_arg, Config)

        # Verify attributes of the passed Config object
        self.assertEqual(config_arg.cycles, 3)
        self.assertEqual(config_arg.initial_translation_type_str, "fr_to_en")
        self.assertEqual(config_arg.initial_translation_type, TypeOfTranslation.fr_to_en)
        self.assertEqual(config_arg.pooling_dir, "test_pool")
        self.assertEqual(config_arg.model_dir, "test_model")
        self.assertEqual(config_arg.log_dir, "test_log")
        self.assertFalse(config_arg.use_dummy_model) # model_dir is not "dummy"

        # --- Test default arguments ---
        mock_main.reset_mock()
        test_args = ["main.py"]  # Use default
        with patch('sys.argv', test_args):
             main.main_cli()

        # Assert called once, then check the config object passed for defaults
        mock_main.assert_called_once()
        call_args_default, call_kwargs_default = mock_main.call_args
        self.assertIn('config', call_kwargs_default)
        config_arg_default = call_kwargs_default['config']
        self.assertIsInstance(config_arg_default, Config)

        # Verify default attributes
        self.assertEqual(config_arg_default.cycles, 1)
        self.assertEqual(config_arg_default.initial_translation_type_str, "en_to_fr")
        self.assertEqual(config_arg_default.initial_translation_type, TypeOfTranslation.en_to_fr)
        self.assertEqual(config_arg_default.pooling_dir, "./data/pooling")
        self.assertEqual(config_arg_default.model_dir, "./models")
        self.assertEqual(config_arg_default.log_dir, "./logs")
        self.assertFalse(config_arg_default.use_dummy_model) # Default model_dir is not "dummy"