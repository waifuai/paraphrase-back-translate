# tests/test_log_single_file.py
import os
import shutil
import unittest
from unittest.mock import patch
import log_single_file
from config import Config # Import Config

class TestLogSingleFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_log"
        self.log_dir = os.path.join(self.test_dir, "logs")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('log_single_file.update_custom_log.update_custom_log')
    def test_log_single_cycle(self, mock_update_log):
        # Create a config object pointing to the test directory
        test_config = Config(
            cycles=0, # Not used
            initial_translation_type_str="en_to_fr", # Not used
            pooling_dir="", # Not used
            model_dir="", # Not used
            log_dir="logs", # Relative log dir name
            local_base_dir=self.test_dir # Base for log dir
        )
        expected_log_dir = test_config.local_log_dir_path
        expected_counter_file = test_config.cycle_counter_filepath

        # --- First cycle ---
        log_single_file.log_single_cycle(config=test_config)

        # Check counter file exists and has correct content
        self.assertTrue(os.path.exists(expected_counter_file))
        with open(expected_counter_file, "r") as f:
            self.assertEqual(int(f.read().strip()), 1)

        # Check mock call
        self.assertEqual(mock_update_log.call_count, 1)
        args, kwargs = mock_update_log.call_args
        self.assertEqual(kwargs['y'], 1)
        self.assertEqual(kwargs['name'], "n_cycles")
        self.assertEqual(kwargs['log_dir'], expected_log_dir) # Check log dir passed correctly

        # --- Second cycle, check increment ---
        mock_update_log.reset_mock()
        log_single_file.log_single_cycle(config=test_config) # Call again with same config

        # Check counter file content
        with open(expected_counter_file, "r") as f:
            self.assertEqual(int(f.read().strip()), 2)

        # Check mock call argument
        args, kwargs = mock_update_log.call_args
        self.assertEqual(kwargs['y'], 2)

    # Patch update_custom_log here too, as log_single_cycle calls it
    @patch('log_single_file.update_custom_log.update_custom_log')
    def test_log_directory_creation(self, mock_update_log):
        # Create config with a different log_dir name
        test_config_new_log = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir="", model_dir="",
            log_dir="new_logs", # Different log directory name
            local_base_dir=self.test_dir
        )
        expected_new_log_dir = test_config_new_log.local_log_dir_path

        # Call the function
        log_single_file.log_single_cycle(config=test_config_new_log)

        # Assert the new directory was created
        self.assertTrue(os.path.exists(expected_new_log_dir))
        # Mock should have been called once (to prevent errors if not patched)
        mock_update_log.assert_called_once()