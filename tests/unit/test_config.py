"""
Unit tests for the config module.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from src.config import Config, TypeOfTranslation, Provider, DEFAULT_GEMINI_MODEL, DEFAULT_OPENROUTER_MODEL


class TestTypeOfTranslation:
    """Test the TypeOfTranslation enum."""

    def test_enum_values(self):
        """Test that enum values are correct."""
        assert TypeOfTranslation.en_to_fr.value == 1
        assert TypeOfTranslation.fr_to_en.value == 2

    def test_enum_names(self):
        """Test that enum names are correct."""
        assert TypeOfTranslation.en_to_fr.name == "en_to_fr"
        assert TypeOfTranslation.fr_to_en.name == "fr_to_en"


class TestProvider:
    """Test the Provider enum."""

    def test_enum_values(self):
        """Test that enum values are correct."""
        assert Provider.openrouter.value == "openrouter"
        assert Provider.gemini.value == "gemini"


class TestConfig:
    """Test the Config dataclass."""

    def test_config_creation_minimal(self):
        """Test creating a Config with minimal required parameters."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data/pooling",
                log_dir="./logs"
            )

            assert config.cycles == 1
            assert config.initial_translation_type_str == "en_to_fr"
            assert config.pooling_dir == "./data/pooling"
            assert config.log_dir == "./logs"
            assert config.initial_translation_type == TypeOfTranslation.en_to_fr

    def test_config_creation_full(self):
        """Test creating a Config with all parameters."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value="test-model"):
            config = Config(
                cycles=2,
                initial_translation_type_str="fr_to_en",
                pooling_dir="./test_data",
                log_dir="./test_logs",
                gemini_model_name="custom-gemini",
                api_key_path="~/.custom_key",
                provider=Provider.openrouter,
                model_name="custom-model"
            )

            assert config.cycles == 2
            assert config.initial_translation_type_str == "fr_to_en"
            assert config.pooling_dir == "./test_data"
            assert config.log_dir == "./test_logs"
            assert config.gemini_model_name == "custom-gemini"
            assert config.api_key_path == "~/.custom_key"
            assert config.provider == Provider.openrouter
            assert config.model_name == "custom-model"
            assert config.initial_translation_type == TypeOfTranslation.fr_to_en

    def test_invalid_translation_type(self):
        """Test that invalid translation type raises ValueError."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            with pytest.raises(ValueError, match="Invalid translation_type: invalid"):
                Config(
                    cycles=1,
                    initial_translation_type_str="invalid",
                    pooling_dir="./data",
                    log_dir="./logs"
                )

    @patch('src.config.os.getenv')
    def test_load_api_key_from_env_gemini(self, mock_getenv):
        """Test loading API key from GEMINI_API_KEY environment variable."""
        mock_getenv.return_value = "test-gemini-key"

        with patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.api_key == "test-gemini-key"

    @patch('src.config.os.getenv')
    def test_load_api_key_from_env_google(self, mock_getenv):
        """Test loading API key from GOOGLE_API_KEY environment variable."""
        mock_getenv.side_effect = lambda key: "test-google-key" if key == "GOOGLE_API_KEY" else None

        with patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.api_key == "test-google-key"

    @patch('src.config.os.getenv')
    @patch('src.config.os.path.expanduser')
    def test_load_api_key_from_file(self, mock_expanduser, mock_getenv):
        """Test loading API key from file."""
        mock_getenv.return_value = None
        mock_expanduser.return_value = "/mocked/path/.api-key"

        mock_file_content = "file-api-key"

        with patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL), \
             patch('builtins.open', mock_open(read_data=mock_file_content)):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.api_key == "file-api-key"

    @patch('src.config.os.getenv')
    @patch('src.config.os.path.expanduser')
    def test_load_api_key_file_not_found(self, mock_expanduser, mock_getenv):
        """Test that FileNotFoundError is raised when API key file doesn't exist."""
        mock_getenv.return_value = None
        mock_expanduser.return_value = "/nonexistent/path/.api-key"

        with patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL), \
             patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError, match="API key not found"):
                Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="./logs"
                )

    @patch('src.config.os.getenv')
    @patch('src.config.os.path.expanduser')
    def test_load_api_key_empty_file(self, mock_expanduser, mock_getenv):
        """Test that ValueError is raised when API key file is empty."""
        mock_getenv.return_value = None
        mock_expanduser.return_value = "/mocked/path/.api-key"

        with patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL), \
             patch('builtins.open', mock_open(read_data="")):
            with pytest.raises(ValueError, match="API key file is empty"):
                Config(
                    cycles=1,
                    initial_translation_type_str="en_to_fr",
                    pooling_dir="./data",
                    log_dir="./logs"
                )

    def test_resolve_model_name_explicit(self):
        """Test model name resolution with explicit model_name."""
        with patch('src.config.Config._load_api_key'):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                model_name="explicit-model"
            )

            assert config.resolved_model_name == "explicit-model"

    @patch('src.config.Path.is_file')
    def test_resolve_model_name_openrouter_file(self, mock_is_file):
        """Test model name resolution from OpenRouter dotfile."""
        mock_is_file.return_value = True

        with patch('src.config.Config._load_api_key'), \
             patch('pathlib.Path.read_text', return_value="file-model"):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                provider=Provider.openrouter
            )

            assert config.resolved_model_name == "file-model"

    @patch('src.config.Path.is_file')
    def test_resolve_model_name_gemini_file(self, mock_is_file):
        """Test model name resolution from Gemini dotfile."""
        mock_is_file.return_value = True

        with patch('src.config.Config._load_api_key'), \
             patch('pathlib.Path.read_text', return_value="gemini-file-model"):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                provider=Provider.gemini
            )

            assert config.resolved_model_name == "gemini-file-model"

    def test_resolve_model_name_gemini_fallback(self):
        """Test model name resolution fallback to gemini_model_name for Gemini provider."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Path.is_file', return_value=False):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                provider=Provider.gemini,
                gemini_model_name="custom-gemini-model"
            )

            assert config.resolved_model_name == "custom-gemini-model"

    def test_resolve_model_name_defaults(self):
        """Test model name resolution using provider defaults."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Path.is_file', return_value=False):
            # Test OpenRouter default
            config_openrouter = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                provider=Provider.openrouter
            )
            assert config_openrouter.resolved_model_name == DEFAULT_OPENROUTER_MODEL

            # Test Gemini default
            config_gemini = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs",
                provider=Provider.gemini
            )
            assert config_gemini.resolved_model_name == DEFAULT_GEMINI_MODEL

    def test_path_generation_methods(self):
        """Test path generation methods."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="/test/pooling",
                log_dir="logs"
            )

            # Test input directory paths
            assert config.get_input_dir(TypeOfTranslation.en_to_fr) == os.path.join("/test/pooling", "input_pool")
            assert config.get_input_dir(TypeOfTranslation.fr_to_en) == os.path.join("/test/pooling", "french_pool")

            # Test output directory paths
            assert config.get_output_dir(TypeOfTranslation.en_to_fr) == os.path.join("/test/pooling", "french_pool")
            assert config.get_output_dir(TypeOfTranslation.fr_to_en) == os.path.join("/test/pooling", "output_pool")

            # Test completed directory paths
            assert config.get_completed_dir(TypeOfTranslation.en_to_fr) == os.path.join("/test/pooling", "input_pool_completed")
            assert config.get_completed_dir(TypeOfTranslation.fr_to_en) == os.path.join("/test/pooling", "french_pool_completed")

    @patch('src.config.os.makedirs')
    def test_log_filepath_creation(self, mock_makedirs):
        """Test that log directory is created when accessing log_filepath."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="logs",
                local_base_dir="/test"
            )

            log_path = config.log_filepath
            expected_path = os.path.join("/test", "logs", "backtranslate.log")
            assert log_path == expected_path
            expected_makedirs_path = os.path.join("/test", "logs")
            mock_makedirs.assert_called_once_with(expected_makedirs_path, exist_ok=True)


class TestConfigDefaults:
    """Test Config default values."""

    def test_default_provider(self):
        """Test that default provider is openrouter."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.provider == Provider.openrouter

    def test_default_api_key_path(self):
        """Test that default API key path is correct."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.api_key_path == "~/.api-gemini"

    def test_default_local_base_dir(self):
        """Test that default local_base_dir is current directory."""
        with patch('src.config.Config._load_api_key'), \
             patch('src.config.Config._resolve_model_name', return_value=DEFAULT_GEMINI_MODEL):
            config = Config(
                cycles=1,
                initial_translation_type_str="en_to_fr",
                pooling_dir="./data",
                log_dir="./logs"
            )

            assert config.local_base_dir == "."