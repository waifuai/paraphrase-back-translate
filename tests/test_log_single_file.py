# tests/test_log_single_file.py
import os
import shutil
import unittest
from unittest.mock import patch
import log_single_file

class TestLogSingleFile(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_log"
        self.log_dir = os.path.join(self.test_dir, "logs")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('log_single_file.update_custom_log.update_custom_log')
    def test_log_single_cycle(self, mock_update_log):
        # First cycle
        log_single_file.log_single_cycle(log_dir_stem="logs", local_base_dir=self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.log_dir, "cycle_count.txt")))
        with open(os.path.join(self.log_dir, "cycle_count.txt"), "r") as f:
            self.assertEqual(int(f.read().strip()), 1)
        self.assertEqual(mock_update_log.call_count, 1) # Check that it was called.
        args, kwargs = mock_update_log.call_args
        self.assertEqual(kwargs['y'], 1) # Check the argument.
        self.assertEqual(kwargs['name'], "n_cycles")
        self.assertEqual(kwargs['log_dir'], self.log_dir)

        # Second cycle, check increment
        mock_update_log.reset_mock() #reset
        log_single_file.log_single_cycle(log_dir_stem="logs", local_base_dir=self.test_dir)
        with open(os.path.join(self.log_dir, "cycle_count.txt"), "r") as f:
            self.assertEqual(int(f.read().strip()), 2)
        args, kwargs = mock_update_log.call_args
        self.assertEqual(kwargs['y'], 2) # Check the incremented argument.

    def test_log_directory_creation(self):
        log_single_file.log_single_cycle(log_dir_stem="new_logs", local_base_dir=self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "new_logs")))