# tests/test_log_single_file.py
import os
import shutil
import unittest
import logging
from unittest.mock import patch, MagicMock
import log_single_file
from config import Config # Import Config

# Prevent the logger from writing to console during tests
# logging.disable(logging.CRITICAL)

class TestLogSingleFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_log"
        self.log_dir_name = "logs"
        self.log_dir_path = os.path.join(self.test_dir, self.log_dir_name)
        # Ensure the base test directory exists, log dir creation is handled by Config/function
        os.makedirs(self.test_dir, exist_ok=True)

        # Reset the in-memory cycle counter before each test
        log_single_file._current_cycle_count = 0
        # Reset logger configuration status
        log_single_file._logger_configured = False

        # Clean up log file if it exists from previous runs
        self.log_filepath = os.path.join(self.log_dir_path, "backtranslate.log")
        if os.path.exists(self.log_filepath):
            os.remove(self.log_filepath)
        # Ensure log directory does not exist before test if testing creation
        if os.path.exists(self.log_dir_path):
             shutil.rmtree(self.log_dir_path)


    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # Re-enable logging if it was disabled
        # logging.disable(logging.NOTSET)


    # Removed patch for update_custom_log and FileHandler for this test
    # @patch('log_single_file.logging.FileHandler') # No longer needed as we check file content
    def test_log_single_cycle(self): # Removed mock args
        # Create a config object pointing to the test directory
        test_config = Config(
            cycles=0, # Not used
            initial_translation_type_str="en_to_fr", # Not used
            pooling_dir="", # Not used
            log_dir=self.log_dir_name, # Relative log dir name
            local_base_dir=self.test_dir # Base for log dir
        )
        expected_log_filepath = os.path.join(self.log_dir_path, "backtranslate.log")

        # Set level on the mock handler instance
        mock_file_handler.return_value.level = logging.INFO

        # --- First cycle ---
        log_single_file.log_single_cycle(config=test_config)

        # Check logger configuration was called
        mock_file_handler.assert_called_once_with(expected_log_filepath)
        self.assertTrue(log_single_file._logger_configured) # Check flag

        # update_custom_log is no longer mocked here, so cannot assert on it directly
        # We will check the log file content instead

        # --- Second cycle, check increment ---
        # mock_update_log.reset_mock() # No longer needed
        # Logger should not be reconfigured
        mock_file_handler.reset_mock()

        log_single_file.log_single_cycle(config=test_config) # Call again with same config

        # Check logger was NOT reconfigured
        mock_file_handler.assert_not_called()

        # update_custom_log is no longer mocked here, cannot assert directly

        # Check log file content (now primary verification)
        self.assertTrue(os.path.exists(expected_log_filepath))
        with open(expected_log_filepath, "r") as f:
            log_content = f.read()
            self.assertIn("Cycle 1 completed", log_content)
            self.assertIn("Cycle 2 completed", log_content)
            self.assertIn("Metric - Step: 1, Name: cycle_completed, Value: 1", log_content)
            self.assertIn("Metric - Step: 2, Name: cycle_completed, Value: 2", log_content)


    @patch('log_single_file.logging.FileHandler')
    def test_log_directory_creation(self, mock_file_handler):
         # Config ensures directory exists via local_log_dir_path property
        test_config_new_log = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir="",
            log_dir="new_logs_dir", # Different log directory name
            local_base_dir=self.test_dir
        )
        expected_new_log_dir = test_config_new_log.local_log_dir_path
        expected_new_log_filepath = os.path.join(expected_new_log_dir, "backtranslate.log")

        # Set level on the mock handler instance
        mock_file_handler.return_value.level = logging.INFO

        # Ensure dir doesn't exist before call
        if os.path.exists(expected_new_log_dir):
            shutil.rmtree(expected_new_log_dir)
        self.assertFalse(os.path.exists(expected_new_log_dir))

        # Call the function - local_log_dir_path property access will create dir
        log_single_file.log_single_cycle(config=test_config_new_log)

        # Assert the new directory was created (by Config property)
        self.assertTrue(os.path.exists(expected_new_log_dir))
        # Assert FileHandler was called with the correct path
        mock_file_handler.assert_called_once_with(expected_new_log_filepath)