"""
Unit tests for the utils module.
"""

import os
import tempfile
import shutil
from unittest.mock import patch
from pathlib import Path

import pytest

from src.utils import (
    sh,
    is_dir_exist,
    is_file_has_size,
    is_files_left_in_dir,
    get_random_file_from_dir
)


class TestSh:
    """Test the sh function."""

    @patch('src.utils.subprocess.run')
    def test_sh_success(self, mock_run):
        """Test successful shell command execution."""
        mock_run.return_value.returncode = 0

        # Should not raise exception
        sh("echo 'test'")

        # The cwd should be the src directory, not the test directory
        import src.utils
        expected_cwd = os.path.dirname(src.utils.__file__)
        mock_run.assert_called_once_with(['echo', "'test'"], check=True, cwd=expected_cwd)

    @patch('src.utils.subprocess.run')
    def test_sh_failure(self, mock_run):
        """Test shell command execution failure."""
        mock_run.side_effect = Exception("Command failed")

        with pytest.raises(Exception, match="Command failed"):
            sh("failing_command")


class TestIsDirExist:
    """Test the is_dir_exist function."""

    def test_existing_directory(self):
        """Test with an existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert is_dir_exist(temp_dir) is True

    def test_nonexistent_directory(self):
        """Test with a nonexistent directory."""
        assert is_dir_exist("/nonexistent/directory") is False

    def test_file_as_directory(self):
        """Test with a file instead of directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            assert is_dir_exist(temp_file.name) is False


class TestIsFileHasSize:
    """Test the is_file_has_size function."""

    def test_existing_file_correct_size(self):
        """Test with existing file of correct size."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"12345")  # 5 bytes
            temp_file.flush()

            assert is_file_has_size(temp_file.name, 5) is True

    def test_existing_file_wrong_size(self):
        """Test with existing file of wrong size."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"123")  # 3 bytes
            temp_file.flush()

            assert is_file_has_size(temp_file.name, 5) is False

    def test_nonexistent_file(self):
        """Test with nonexistent file."""
        assert is_file_has_size("/nonexistent/file", 10) is False


class TestIsFilesLeftInDir:
    """Test the is_files_left_in_dir function."""

    def test_directory_with_files(self):
        """Test directory containing files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file in the directory
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("content")

            assert is_files_left_in_dir(temp_dir) is True

    def test_empty_directory(self):
        """Test empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert is_files_left_in_dir(temp_dir) is False

    def test_nonexistent_directory(self):
        """Test nonexistent directory."""
        assert is_files_left_in_dir("/nonexistent/directory") is False

    def test_directory_with_only_subdirectories(self):
        """Test directory with only subdirectories (no files)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)

            assert is_files_left_in_dir(temp_dir) is False


class TestGetRandomFileFromDir:
    """Test the get_random_file_from_dir function."""

    def test_get_random_file_success(self):
        """Test successfully getting a random file from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple files
            files = []
            for i in range(3):
                file_path = os.path.join(temp_dir, f"test_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"content {i}")
                files.append(f"test_{i}.txt")

            # Should return one of the files
            result = get_random_file_from_dir(temp_dir)
            assert result in files
            assert os.path.exists(os.path.join(temp_dir, result))

    def test_get_random_file_empty_directory(self):
        """Test getting random file from empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(RuntimeError, match=r"No files found in directory: .*"):
                get_random_file_from_dir(temp_dir)

    def test_get_random_file_nonexistent_directory(self):
        """Test getting random file from nonexistent directory."""
        nonexistent_dir = "/nonexistent/directory"
        with pytest.raises(RuntimeError, match=f"No files found in directory: {nonexistent_dir}"):
            get_random_file_from_dir(nonexistent_dir)

    def test_get_random_file_with_subdirectories(self):
        """Test that subdirectories are ignored, only files are considered."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file and a subdirectory
            file_path = os.path.join(temp_dir, "test.txt")
            with open(file_path, "w") as f:
                f.write("content")

            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)

            # Should return the file, not the subdirectory
            result = get_random_file_from_dir(temp_dir)
            assert result == "test.txt"



class TestUtilsIntegration:
    """Integration tests for utils functions."""

    def test_directory_workflow(self):
        """Test typical directory workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initially empty
            assert is_files_left_in_dir(temp_dir) is False

            # Add a file
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("content")

            # Now has files
            assert is_files_left_in_dir(temp_dir) is True

            # Can get random file
            random_file = get_random_file_from_dir(temp_dir)
            assert random_file == "test.txt"

            # File has correct size
            assert is_file_has_size(test_file, 7) is True  # "content" is 7 bytes

    def test_file_operations_workflow(self):
        """Test file operations workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files of different sizes
            small_file = os.path.join(temp_dir, "small.txt")
            large_file = os.path.join(temp_dir, "large.txt")

            with open(small_file, "w") as f:
                f.write("small")

            with open(large_file, "w") as f:
                f.write("this is a larger file content")

            # Check sizes
            assert is_file_has_size(small_file, 5) is True
            assert is_file_has_size(large_file, 29) is True  # "this is a larger file content" = 29 chars

            # Directory should have files
            assert is_files_left_in_dir(temp_dir) is True

            # Random file should be one of the two
            random_file = get_random_file_from_dir(temp_dir)
            assert random_file in ["small.txt", "large.txt"]