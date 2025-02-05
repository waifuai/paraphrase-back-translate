# tests/test_translate.py
import os
import shutil
import unittest
import utils
import translate_single_file as tsf


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
        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir,
        )
        translated_file_path = os.path.join(
            self.pooling_dir, "french_pool", self.input_file
        )
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "dlroW olleH")
        # Check file movement
        self.assertFalse(os.path.exists(self.input_file_path))  # Should be moved
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.pooling_dir, "input_pool_completed", self.input_file
                )
            )
        )

    def test_translation_fr_to_en_dummy(self):
        # Set up for fr_to_en test
        self._create_input_file("Bonjour le monde", pool="french_pool")
        input_file_path_fr = os.path.join(
            self.pooling_dir, "french_pool", self.input_file
        )

        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.fr_to_en,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir,
        )
        translated_file_path = os.path.join(
            self.pooling_dir, "output_pool", self.input_file
        )
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "ednom el ruojnoB")

        # Check file movement
        self.assertFalse(os.path.exists(input_file_path_fr))  # Should be moved
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.pooling_dir, "french_pool_completed", self.input_file
                )
            )
        )

    def test_missing_model_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            tsf.translate_single_file(
                translation_type=utils.TypeOfTranslation.en_to_fr,
                pooling_dir=self.pooling_dir,
                model_dir="./nonexistent_model_dir",  # Point to a dir that doesn't exist
            )

    def test_empty_input_file(self):
        self._create_input_file("")  # Create an empty input file
        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir,
        )
        translated_file_path = os.path.join(
            self.pooling_dir, "french_pool", self.input_file
        )
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "")  # Reversed empty string is still empty

    def test_varied_input_text(self):
        self._create_input_file("Hello, world! 123")
        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir,
        )
        translated_file_path = os.path.join(
            self.pooling_dir, "french_pool", self.input_file
        )
        with open(translated_file_path, "r") as f:
            self.assertEqual(f.read(), "321 !dlrow ,olleH")

    def test_local_file_creation(self):
        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir
        )
        self.assertTrue(os.path.exists(self.input_file)) #check if it exists in current directory
        with open(self.input_file, 'r') as f:
            self.assertEqual(f.read(), "Hello World")