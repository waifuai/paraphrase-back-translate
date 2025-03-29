# tests/test_translate.py
import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import utils
from config import Config, TypeOfTranslation # Import Config and Enum
import translate_single_file as tsf


# Patch the trax imports within the translate_single_file module
# This prevents the problematic trax code from loading during test discovery
@patch('translate_single_file.trax.supervised.decoding', MagicMock())
@patch('translate_single_file.trax.data', MagicMock())
@patch('translate_single_file.trax', MagicMock())
class TestTranslateSingleFile(unittest.TestCase):
    def setUp(self):
        # Create temporary directories for each test.
        self.test_dir = "test_temp_translate"
        self.pooling_dir = os.path.join(self.test_dir, "pooling")
        self.model_dir = "dummy"  # Default to dummy for most tests.

        # Create directory structure.
        for subdir in ["input_pool", "french_pool", "output_pool"]:
            os.makedirs(os.path.join(self.pooling_dir, subdir), exist_ok=True)

        self.input_file = "test.txt"
        self.input_file_path = os.path.join(
            self.pooling_dir, "input_pool", self.input_file
        )
        with open(self.input_file_path, "w") as f:
            f.write("Hello World")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_input_file(self, content, pool="input_pool"):
        """Helper function to create input files."""
        file_path = os.path.join(self.pooling_dir, pool, self.input_file)
        with open(file_path, "w") as f:
            f.write(content)


    def test_translation_en_to_fr_dummy(self):
        # Create config for this test
        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr", # Not used directly
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir, # Should be "dummy"
            log_dir="" # Not used
        )
        current_type = TypeOfTranslation.en_to_fr

        # Call the function
        tsf.translate_single_file(
            config=test_config,
            current_translation_type=current_type
        )

        # Define expected paths using config
        expected_output_dir = test_config.get_output_dir(current_type) # french_pool
        expected_completed_dir = test_config.get_completed_dir(current_type) # input_pool_completed
        translated_file_path = os.path.join(expected_output_dir, self.input_file)
        completed_file_path = os.path.join(expected_completed_dir, self.input_file)
        original_input_path = os.path.join(test_config.get_input_dir(current_type), self.input_file)

        # Check translation result
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "dlroW olleH") # Dummy reverse

        # Check file movement
        self.assertFalse(os.path.exists(original_input_path)) # Original should be moved
        self.assertTrue(os.path.exists(completed_file_path)) # Should exist in completed dir


    def test_translation_fr_to_en_dummy(self):
        # Create config for this test
        test_config = Config(
            cycles=0, initial_translation_type_str="fr_to_en", # Not used directly
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir, # Should be "dummy"
            log_dir="" # Not used
        )
        current_type = TypeOfTranslation.fr_to_en

        # Set up input file in the correct pool
        input_content = "Bonjour le monde"
        self._create_input_file(input_content, pool="french_pool")
        original_input_path = os.path.join(test_config.get_input_dir(current_type), self.input_file)

        # Call the function
        tsf.translate_single_file(
            config=test_config,
            current_translation_type=current_type
        )

        # Define expected paths using config
        expected_output_dir = test_config.get_output_dir(current_type) # output_pool
        expected_completed_dir = test_config.get_completed_dir(current_type) # french_pool_completed
        translated_file_path = os.path.join(expected_output_dir, self.input_file)
        completed_file_path = os.path.join(expected_completed_dir, self.input_file)

        # Check translation result
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "ednom el ruojnoB") # Dummy reverse

        # Check file movement
        self.assertFalse(os.path.exists(original_input_path)) # Original should be moved
        self.assertTrue(os.path.exists(completed_file_path)) # Should exist in completed dir


    def test_missing_model_raises_error(self):
        # Create config pointing to a non-dummy, non-existent model dir
        test_config_missing = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir,
            model_dir="./nonexistent_model_dir", # Non-dummy, non-existent
            log_dir=""
        )
        current_type = TypeOfTranslation.en_to_fr

        with self.assertRaises(FileNotFoundError):
            tsf.translate_single_file(
                config=test_config_missing,
                current_translation_type=current_type
            )


    def test_empty_input_file(self):
        self._create_input_file("")  # Create an empty input file

        # Create config
        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir, # dummy
            log_dir=""
        )
        current_type = TypeOfTranslation.en_to_fr

        # Call function
        tsf.translate_single_file(
            config=test_config,
            current_translation_type=current_type
        )

        # Define expected paths
        expected_output_dir = test_config.get_output_dir(current_type)
        translated_file_path = os.path.join(expected_output_dir, self.input_file)

        # Check result
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "")  # Reversed empty string is still empty


    def test_varied_input_text(self):
        input_text = "Hello, world! 123"
        self._create_input_file(input_text)

        # Create config
        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir, # dummy
            log_dir=""
        )
        current_type = TypeOfTranslation.en_to_fr

        # Call function
        tsf.translate_single_file(
            config=test_config,
            current_translation_type=current_type
        )

        # Define expected paths
        expected_output_dir = test_config.get_output_dir(current_type)
        translated_file_path = os.path.join(expected_output_dir, self.input_file)

        # Check result
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "321 !dlrow ,olleH") # Dummy reverse


    def test_local_file_cleanup(self):
        """Tests that the local copy of the input file is removed after processing."""
        # Create config
        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir, # dummy
            log_dir=""
        )
        current_type = TypeOfTranslation.en_to_fr

        # Define the expected local path based on the input filename
        local_copy_path = os.path.basename(self.input_file)

        # Ensure the local file doesn't exist before the call (it shouldn't)
        if os.path.exists(local_copy_path):
             os.remove(local_copy_path)
        self.assertFalse(os.path.exists(local_copy_path))

        # Call function
        tsf.translate_single_file(
            config=test_config,
            current_translation_type=current_type
        )

        # Assert that the local copy was created during the process (checked implicitly by success)
        # Assert that the local copy is REMOVED by the end of the function (_move_files cleanup)
        self.assertFalse(os.path.exists(local_copy_path),
                         f"Local copy '{local_copy_path}' was not cleaned up.")