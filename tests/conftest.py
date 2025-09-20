"""
Test configuration and fixtures for pytest.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from src.config import Config, TypeOfTranslation, Provider, DEFAULT_GEMINI_MODEL


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock Config object for testing."""
    with patch('src.config.Config._load_api_key'), \
         patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
        config = Config(
            cycles=1,
            initial_translation_type_str="en_to_fr",
            pooling_dir=os.path.join(temp_dir, "pooling"),
            log_dir="logs",
            local_base_dir=temp_dir
        )
        yield config


@pytest.fixture
def sample_text_files(temp_dir):
    """Create sample text files for testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"test_{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"This is test content {i}. It has multiple sentences.\nSecond line here.")
        files.append(file_path)
    return files


@pytest.fixture
def pooling_structure(temp_dir):
    """Create the directory structure for pooling tests."""
    pooling_dir = os.path.join(temp_dir, "pooling")
    subdirs = [
        "input_pool",
        "french_pool",
        "output_pool",
        "input_pool_completed",
        "french_pool_completed"
    ]

    for subdir in subdirs:
        os.makedirs(os.path.join(pooling_dir, subdir), exist_ok=True)

    # Add some sample files
    input_pool = os.path.join(pooling_dir, "input_pool")
    for i in range(2):
        file_path = os.path.join(input_pool, f"sample_{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Sample English text {i} for translation testing.")

    return pooling_dir


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before each test."""
    import logging
    import gc
    from src import log_single_file

    # Reset the global flag
    log_single_file._logger_configured = False

    # Clear existing handlers and force garbage collection
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # Force garbage collection to release file handles
    gc.collect()

    # Reset cycle counter
    log_single_file._current_cycle_count = 0

    yield

    # Cleanup after test
    log_single_file._logger_configured = False
    log_single_file._current_cycle_count = 0

    # Clear handlers again after test
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()
    gc.collect()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        'GEMINI_API_KEY': 'test-gemini-key',
        'GOOGLE_API_KEY': 'test-google-key'
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def mock_api_key_file(temp_dir):
    """Create a mock API key file."""
    api_key_file = os.path.join(temp_dir, ".api-gemini")
    with open(api_key_file, "w", encoding="utf-8") as f:
        f.write("file-api-key-content")

    return api_key_file


@pytest.fixture
def mock_model_files(temp_dir):
    """Create mock model configuration files."""
    gemini_model_file = os.path.join(temp_dir, ".model-gemini")
    openrouter_model_file = os.path.join(temp_dir, ".model-openrouter")

    with open(gemini_model_file, "w", encoding="utf-8") as f:
        f.write("gemini-pro")

    with open(openrouter_model_file, "w", encoding="utf-8") as f:
        f.write("deepseek/deepseek-chat-v3")

    return {
        'gemini': gemini_model_file,
        'openrouter': openrouter_model_file
    }


@pytest.fixture
def mock_home_directory(mock_model_files, temp_dir):
    """Mock the home directory for testing dotfiles."""
    with patch('src.config.Path.home', return_value=Path(temp_dir)):
        yield temp_dir


@pytest.fixture
def mock_logging():
    """Mock logging functionality to avoid file handle issues."""
    with patch('src.log_single_file.setup_logging'), \
         patch('src.update_custom_log.update_custom_log'), \
         patch('src.log_single_file.logger'):
        yield