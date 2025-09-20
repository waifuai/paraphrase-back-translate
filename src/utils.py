"""
Utility functions with comprehensive type hints and error handling.
"""

import subprocess
import os
import random
from typing import List, Optional
from pathlib import Path


def sh(command: str, cwd: Optional[str] = None) -> None:
    """
    Executes a shell command.

    Args:
        command: The shell command to execute
        cwd: Working directory for command execution. Defaults to the directory containing this file.

    Raises:
        subprocess.CalledProcessError: If the command fails
        RuntimeError: If command execution fails
    """
    try:
        if cwd is None:
            cwd = os.path.dirname(__file__) or None
        subprocess.run(command.split(), check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed with exit code {e.returncode}: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error executing command '{command}': {e}") from e


def is_dir_exist(dir_path: str) -> bool:
    """
    Checks if a directory exists and is accessible.

    Args:
        dir_path: Path to the directory to check

    Returns:
        True if directory exists and is accessible, False otherwise
    """
    try:
        return os.path.isdir(dir_path)
    except (OSError, ValueError):
        return False


def is_file_has_size(file_path: str, expected_file_size: int) -> bool:
    """
    Checks if a file exists and has the expected size.

    Args:
        file_path: Path to the file to check
        expected_file_size: Expected size in bytes

    Returns:
        True if file exists and has expected size, False otherwise
    """
    try:
        return os.path.getsize(file_path) == expected_file_size
    except (FileNotFoundError, OSError):
        return False


def is_files_left_in_dir(dir_path: str) -> bool:
    """
    Checks if a directory contains any files (not subdirectories).

    Args:
        dir_path: Path to the directory to check

    Returns:
        True if directory exists and contains files, False otherwise
    """
    if not is_dir_exist(dir_path):
        return False

    try:
        return any(
            os.path.isfile(os.path.join(dir_path, item))
            for item in os.listdir(dir_path)
        )
    except OSError:
        return False


def get_random_file_from_dir(dir_path: str) -> str:
    """
    Returns a random file from a directory.

    Args:
        dir_path: Path to the directory to search

    Returns:
        Name of a randomly selected file

    Raises:
        RuntimeError: If directory doesn't exist or contains no files
        OSError: If directory cannot be accessed
    """
    if not is_dir_exist(dir_path):
        raise RuntimeError(f"Directory does not exist: {dir_path}")

    try:
        all_items = os.listdir(dir_path)
    except OSError as e:
        raise RuntimeError(f"Cannot access directory '{dir_path}': {e}") from e

    files: List[str] = [
        item for item in all_items
        if os.path.isfile(os.path.join(dir_path, item))
    ]

    if not files:
        raise RuntimeError(f"No files found in directory: {dir_path}")

    return random.choice(files)


def validate_directory(dir_path: str) -> Path:
    """
    Validates and returns a Path object for a directory.

    Args:
        dir_path: Directory path to validate

    Returns:
        Path object for the validated directory

    Raises:
        ValueError: If path is empty or invalid
        FileNotFoundError: If directory doesn't exist
    """
    if not dir_path or not dir_path.strip():
        raise ValueError("Directory path cannot be empty")

    path = Path(dir_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    return path


def ensure_directory_exists(dir_path: str) -> Path:
    """
    Ensures a directory exists, creating it if necessary.

    Args:
        dir_path: Directory path to ensure exists

    Returns:
        Path object for the directory

    Raises:
        ValueError: If path is invalid
        OSError: If directory cannot be created
    """
    if not dir_path or not dir_path.strip():
        raise ValueError("Directory path cannot be empty")

    path = Path(dir_path).resolve()
    path.mkdir(parents=True, exist_ok=True)

    return path
