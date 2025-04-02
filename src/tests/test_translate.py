# tests/test_translate.py
import os
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open
import torch # Import torch
# import utils # No longer needed directly here
from config import Config, TypeOfTranslation # Import Config and Enum
import translate_single_file as tsf

# Mock the transformers imports at the module level
@patch('translate_single_file.AutoTokenizer.from_pretrained')
@patch('translate_single_file.AutoModelForSeq2SeqLM.from_pretrained')
@patch('translate_single_file.DEVICE', torch.device('cpu')) # Patch the DEVICE constant directly
@patch('translate_single_file.utils.get_random_file_from_dir') # Mock random file selection
class TestTranslateSingleFileHF(unittest.TestCase):

    # mock_torch_device is no longer needed as an argument here

    def setUp(self):
        # Create temporary directories for each test.
        self.test_dir = "test_temp_translate_hf"
        self.pooling_dir = os.path.join(self.test_dir, "pooling")
        # self.model_dir = "dummy" # Removed

        # Create directory structure.
        self.input_pool_en = os.path.join(self.pooling_dir, "input_pool")
        self.input_pool_fr = os.path.join(self.pooling_dir, "french_pool")
        self.output_pool_fr = os.path.join(self.pooling_dir, "french_pool") # Same as input_pool_fr
        self.output_pool_en = os.path.join(self.pooling_dir, "output_pool")
        self.completed_pool_en = os.path.join(self.pooling_dir, "input_pool_completed")
        self.completed_pool_fr = os.path.join(self.pooling_dir, "french_pool_completed")

        for pool_path in [self.input_pool_en, self.input_pool_fr, self.output_pool_en,
                          self.completed_pool_en, self.completed_pool_fr]:
             # output_pool_fr is same as input_pool_fr, created implicitly
            os.makedirs(pool_path, exist_ok=True)

        self.input_filename = "test_translate.txt"

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_input_file(self, content, pool_path):
        """Helper function to create input files in specific pool."""
        file_path = os.path.join(pool_path, self.input_filename)
        # Ensure directory exists before writing
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(content)
        return file_path

    def _setup_mocks(self, mock_auto_model, mock_auto_tokenizer): # Removed mock_torch_device
        """Sets up common mocks for model and tokenizer."""
        # mock_torch_device is no longer needed here

        # Mock tokenizer
        mock_tokenizer_instance = MagicMock()
        mock_tokenizer_instance.return_value = MagicMock( # Mock the __call__ method
             input_ids=torch.tensor([[1, 2, 3]]), # Dummy token IDs
             attention_mask=torch.tensor([[1, 1, 1]])
        )
        mock_tokenizer_instance.decode.return_value = "Mock Translated Text" # Mock decode
        mock_auto_tokenizer.return_value = mock_tokenizer_instance

        # Mock model
        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = torch.tensor([[4, 5, 6]]) # Dummy generated tokens
        # Mock the .to() method called after loading
        mock_model_instance.to.return_value = mock_model_instance
        mock_auto_model.return_value = mock_model_instance
        return mock_model_instance, mock_tokenizer_instance # Indented correctly


    def test_translation_en_to_fr(self, mock_get_random_file, mock_device_patch, mock_auto_model, mock_auto_tokenizer): # Renamed mock_device_patch arg
        """Tests successful en_to_fr translation using mocked HF components."""
        # mock_torch_device removed from _setup_mocks call
        mock_model, mock_tokenizer = self._setup_mocks(mock_auto_model, mock_auto_tokenizer)
        mock_get_random_file.return_value = self.input_filename # Control which file is selected

        input_content = "Hello world"
        # Removed duplicate line below
        original_input_path = self._create_input_file(input_content, self.input_pool_en)

        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir, log_dir="logs"
        )
        current_type = TypeOfTranslation.en_to_fr
        expected_model_name = "Helsinki-NLP/opus-mt-en-fr"
        expected_output_dir = test_config.get_output_dir(current_type) # french_pool
        expected_completed_dir = test_config.get_completed_dir(current_type) # input_pool_completed
        translated_file_path = os.path.join(expected_output_dir, self.input_filename)
        completed_file_path = os.path.join(expected_completed_dir, self.input_filename)

        # Call the function
        tsf.translate_single_file(config=test_config, current_translation_type=current_type)

        # --- Assertions ---
        # Model/Tokenizer loading
        mock_auto_tokenizer.assert_called_once_with(expected_model_name)
        mock_auto_model.assert_called_once_with(expected_model_name)
        mock_model.to.assert_called_once_with(torch.device('cpu')) # Check model moved to mocked device

        # Translation calls
        mock_tokenizer.assert_called_once_with(input_content, return_tensors="pt", padding=True, truncation=True, max_length=512)
        mock_model.generate.assert_called_once()
        mock_tokenizer.decode.assert_called_once_with(mock_model.generate.return_value[0], skip_special_tokens=True)

        # File results
        self.assertTrue(os.path.exists(translated_file_path), "Translated file not found")
        with open(translated_file_path, "r", encoding='utf-8') as f:
            self.assertEqual(f.read(), "Mock Translated Text")

        # File movement
        self.assertFalse(os.path.exists(original_input_path), "Original input file was not moved")
        self.assertTrue(os.path.exists(completed_file_path), "Input file not found in completed dir")


    def test_translation_fr_to_en(self, mock_get_random_file, mock_device_patch, mock_auto_model, mock_auto_tokenizer): # Renamed mock_device_patch arg
        """Tests successful fr_to_en translation using mocked HF components."""
        # mock_torch_device removed from _setup_mocks call
        mock_model, mock_tokenizer = self._setup_mocks(mock_auto_model, mock_auto_tokenizer)
        mock_get_random_file.return_value = self.input_filename

        input_content = "Bonjour le monde"
        original_input_path = self._create_input_file(input_content, self.input_pool_fr) # Create in french_pool

        test_config = Config(
            cycles=0, initial_translation_type_str="fr_to_en", # Does not affect this call directly
            pooling_dir=self.pooling_dir, log_dir="logs"
        )
        current_type = TypeOfTranslation.fr_to_en
        expected_model_name = "Helsinki-NLP/opus-mt-fr-en"
        expected_output_dir = test_config.get_output_dir(current_type) # output_pool
        expected_completed_dir = test_config.get_completed_dir(current_type) # french_pool_completed
        translated_file_path = os.path.join(expected_output_dir, self.input_filename)
        completed_file_path = os.path.join(expected_completed_dir, self.input_filename)

        # Call the function
        tsf.translate_single_file(config=test_config, current_translation_type=current_type)

        # --- Assertions ---
        mock_auto_tokenizer.assert_called_once_with(expected_model_name)
        mock_auto_model.assert_called_once_with(expected_model_name)
        mock_model.to.assert_called_once_with(torch.device('cpu'))
        mock_tokenizer.assert_called_once_with(input_content, return_tensors="pt", padding=True, truncation=True, max_length=512)
        mock_model.generate.assert_called_once()
        mock_tokenizer.decode.assert_called_once_with(mock_model.generate.return_value[0], skip_special_tokens=True)

        self.assertTrue(os.path.exists(translated_file_path), "Translated file not found")
        with open(translated_file_path, "r", encoding='utf-8') as f:
            self.assertEqual(f.read(), "Mock Translated Text")

        self.assertFalse(os.path.exists(original_input_path), "Original input file was not moved")
        self.assertTrue(os.path.exists(completed_file_path), "Input file not found in completed dir")


    def test_model_loading_error(self, mock_get_random_file, mock_device_patch, mock_auto_model, mock_auto_tokenizer): # Added mock_auto_tokenizer, renamed mock_device_patch
        """Tests that OSError during model loading is raised."""
        mock_get_random_file.return_value = self.input_filename
        self._create_input_file("Test content", self.input_pool_en)

        # Configure mocks to raise OSError
        mock_auto_tokenizer.side_effect = OSError("Model not found online")
        # No need to mock model if tokenizer fails first

        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir, log_dir="logs"
        )
        current_type = TypeOfTranslation.en_to_fr

        with self.assertRaises(OSError):
            tsf.translate_single_file(config=test_config, current_translation_type=current_type)


    def test_empty_input_file(self, mock_get_random_file, mock_device_patch, mock_auto_model, mock_auto_tokenizer): # Added mock_auto_tokenizer, renamed mock_device_patch
        """Tests handling of an empty input file."""
        # Pass only needed mocks to _setup_mocks
        mock_model, mock_tokenizer = self._setup_mocks(mock_auto_model, mock_auto_tokenizer) # Removed mock_torch_device
        mock_get_random_file.return_value = self.input_filename

        original_input_path = self._create_input_file("", self.input_pool_en) # Empty content

        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir, log_dir="logs"
        )
        current_type = TypeOfTranslation.en_to_fr
        expected_output_dir = test_config.get_output_dir(current_type)
        expected_completed_dir = test_config.get_completed_dir(current_type)
        translated_file_path = os.path.join(expected_output_dir, self.input_filename)
        completed_file_path = os.path.join(expected_completed_dir, self.input_filename)

        # Call function
        tsf.translate_single_file(config=test_config, current_translation_type=current_type)

        # Assertions
        mock_auto_tokenizer.assert_called_once() # Model/tokenizer still loaded
        mock_auto_model.assert_called_once()
        mock_tokenizer.assert_not_called() # Tokenizer __call__ should not be called
        mock_model.generate.assert_not_called() # Generate should not be called
        mock_tokenizer.decode.assert_not_called() # Decode should not be called

        # Check result file is empty
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r", encoding='utf-8') as f:
            self.assertEqual(f.read(), "")

        # Check file movement
        self.assertFalse(os.path.exists(original_input_path))
        self.assertTrue(os.path.exists(completed_file_path))


    def test_translation_error_handling(self, mock_get_random_file, mock_device_patch, mock_auto_model, mock_auto_tokenizer): # Added mock_auto_tokenizer, renamed mock_device_patch
        """Tests handling of an error during the model.generate step."""
        # Pass only needed mocks to _setup_mocks
        mock_model, mock_tokenizer = self._setup_mocks(mock_auto_model, mock_auto_tokenizer) # Removed mock_torch_device
        mock_get_random_file.return_value = self.input_filename
        # Configure model.generate to raise an exception
        mock_model.generate.side_effect = RuntimeError("CUDA out of memory")

        input_content = "This is a test sentence."
        original_input_path = self._create_input_file(input_content, self.input_pool_en)

        test_config = Config(
            cycles=0, initial_translation_type_str="en_to_fr",
            pooling_dir=self.pooling_dir, log_dir="logs"
        )
        current_type = TypeOfTranslation.en_to_fr
        expected_output_dir = test_config.get_output_dir(current_type)
        expected_completed_dir = test_config.get_completed_dir(current_type)
        translated_file_path = os.path.join(expected_output_dir, self.input_filename)
        completed_file_path = os.path.join(expected_completed_dir, self.input_filename)

        # Call function
        tsf.translate_single_file(config=test_config, current_translation_type=current_type)

        # Assertions
        mock_auto_tokenizer.assert_called_once()
        mock_auto_model.assert_called_once()
        mock_tokenizer.assert_called_once() # Tokenizer __call__ is called
        mock_model.generate.assert_called_once() # generate is called (and raises error)
        mock_tokenizer.decode.assert_not_called() # decode is not reached

        # Check result file contains error message
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r", encoding='utf-8') as f:
            self.assertIn("TRANSLATION_ERROR: CUDA out of memory", f.read())

        # Check file movement still happens
        self.assertFalse(os.path.exists(original_input_path))
        self.assertTrue(os.path.exists(completed_file_path))


# Removed dummy tests and local file cleanup test

if __name__ == "__main__":
    unittest.main()