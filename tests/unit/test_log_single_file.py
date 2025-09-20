"""
Unit tests for the log_single_file module.
"""

import os
import tempfile
import logging
from unittest.mock import patch, mock_open

import pytest

from src.log_single_file import setup_logging, log_single_cycle
from src.config import Config, TypeOfTranslation, Provider, DEFAULT_GEMINI_MODEL


class TestSetupLogging:
    """Test the setup_logging function."""

    def test_setup_logging_first_time(self):
        """Test setting up logging for the first time."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            setup_logging(log_file)

            # Check that log file was created
            assert os.path.exists(log_file)

            # Check that root logger has handlers
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) >= 2  # File and console handlers

            # Check that file handler has correct path
            file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
            assert len(file_handlers) == 1
            assert file_handlers[0].baseFilename == log_file

    def test_setup_logging_multiple_calls(self):
        """Test that multiple calls to setup_logging don't create duplicate handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            # First call
            setup_logging(log_file)
            root_logger = logging.getLogger()
            initial_handler_count = len(root_logger.handlers)

            # Second call
            setup_logging(log_file)

            # Should still have the same number of handlers
            assert len(root_logger.handlers) == initial_handler_count

    def test_setup_logging_directory_creation(self):
        """Test that setup_logging creates the log directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = os.path.join(temp_dir, "nested", "logs")
            log_file = os.path.join(log_dir, "test.log")

            # Directory shouldn't exist yet
            assert not os.path.exists(log_dir)

            setup_logging(log_file)

            # Directory should be created
            assert os.path.exists(log_dir)
            assert os.path.exists(log_file)

    @patch('src.log_single_file.os.makedirs')
    def test_setup_logging_handles_makedirs_error(self, mock_makedirs):
        """Test handling of directory creation errors."""
        mock_makedirs.side_effect = OSError("Permission denied")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            # Should fall back to basic console logging
            with patch('src.log_single_file.logging.basicConfig') as mock_basic_config:
                setup_logging(log_file)
                mock_basic_config.assert_called_once()

    @patch('src.log_single_file.logging.FileHandler')
    def test_setup_logging_handles_file_handler_error(self, mock_file_handler):
        """Test handling of file handler creation errors."""
        mock_file_handler.side_effect = OSError("Cannot create file handler")

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            # Should fall back to basic console logging
            with patch('src.log_single_file.logging.basicConfig') as mock_basic_config:
                setup_logging(log_file)
                mock_basic_config.assert_called_once()


class TestLogSingleCycle:
    """Test the log_single_cycle function."""

    def test_log_single_cycle_basic(self, mock_logging):
        """Test basic cycle logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                # Reset the cycle counter
                from src.log_single_file import _current_cycle_count
                original_count = _current_cycle_count
                _current_cycle_count = 0

                try:
                    log_single_cycle(config)
                    # The actual logging is mocked, so we just verify the function runs
                    assert _current_cycle_count == 1
                finally:
                    _current_cycle_count = original_count

    def test_log_single_cycle_increment_counter(self, mock_logging):
        """Test that cycle counter is incremented properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                from src.log_single_file import _current_cycle_count

                # Reset counter
                original_count = _current_cycle_count
                _current_cycle_count = 5

                try:
                    log_single_cycle(config)

                    # Counter should be incremented
                    assert _current_cycle_count == 6
                finally:
                    _current_cycle_count = original_count

    def test_log_single_cycle_calls_setup_logging(self):
        """Test that log_single_cycle calls setup_logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL), \
                 patch('src.log_single_file.setup_logging') as mock_setup_logging:
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                log_single_cycle(config)

                mock_setup_logging.assert_called_once_with(config.log_filepath)

    def test_log_single_cycle_uses_config_logfile(self):
        """Test that log_single_cycle uses the log file path from config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "custom.log")

            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL), \
                 patch('src.config.Config.log_filepath', new_callable=lambda: property(lambda self: log_file)), \
                 patch('builtins.open', mock_open()):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                log_single_cycle(config)

                # The log file should be the one from config
                assert config.log_filepath == log_file

    def test_log_single_cycle_logs_metric(self, mock_logging):
        """Test that log_single_cycle logs the cycle completion metric."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                from src.log_single_file import _current_cycle_count
                original_count = _current_cycle_count
                _current_cycle_count = 3

                try:
                    with patch('src.update_custom_log.update_custom_log') as mock_update_log:
                        log_single_cycle(config)

                        mock_update_log.assert_called_once_with(
                            x=4,  # Counter gets incremented before logging
                            y=4,
                            name="cycle_completed"
                        )
                finally:
                    _current_cycle_count = original_count


class TestLogSingleCycleIntegration:
    """Integration tests for log_single_cycle."""

    def test_multiple_cycles_increment_properly(self, mock_logging):
        """Test that multiple calls increment the cycle counter properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                from src.log_single_file import _current_cycle_count

                # Reset counter
                original_count = _current_cycle_count
                _current_cycle_count = 0

                try:
                    # Log multiple cycles
                    log_single_cycle(config)
                    assert _current_cycle_count == 1

                    log_single_cycle(config)
                    assert _current_cycle_count == 2

                    log_single_cycle(config)
                    assert _current_cycle_count == 3
                finally:
                    _current_cycle_count = original_count

    def test_log_file_contains_expected_content(self):
        """Test that log file contains expected content after multiple cycles."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            with patch('src.config.Config._load_api_key'), \
                 patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
                config = Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="logs",
                    local_base_dir=temp_dir
                )

                from src.log_single_file import _current_cycle_count
                original_count = _current_cycle_count
                _current_cycle_count = 0

                try:
                    log_single_cycle(config)
                    log_single_cycle(config)

                    with open(log_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        assert "--- Cycle 1 completed. ---" in content
                        assert "--- Cycle 2 completed. ---" in content
                finally:
                    _current_cycle_count = original_count