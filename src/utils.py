"""
Utility functions.
"""

import subprocess
import os
import random
from enum import Enum

class TypeOfTranslation(Enum):
    """Represents the direction of translation."""
    en_to_fr = 1
    fr_to_en = 2

def sh(command: str) -> None:
    """Executes a shell command."""
    try:
        subprocess.run(command.split(), check=True, cwd=os.path.dirname(__file__) or None)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def is_dir_exist(dir_path: str) -> bool:
    """Checks if a directory exists."""
    return os.path.isdir(dir_path)

def is_file_has_size(file_path: str, expected_file_size: int) -> bool:
    """Checks if a file exists and has the expected size."""
    try:
        return os.path.getsize(file_path) == expected_file_size
    except FileNotFoundError:
        return False

def is_files_left_in_dir(dir_path: str) -> bool:
    """Checks if a directory contains any files."""
    return is_dir_exist(dir_path) and len(os.listdir(dir_path)) > 0

def get_random_file_from_dir(dir_path: str) -> str:
    """Returns a random file from a directory."""
    if not is_files_left_in_dir(dir_path):
        raise RuntimeError(f"No files found in directory: {dir_path}")
    return random.choice(os.listdir(dir_path))
