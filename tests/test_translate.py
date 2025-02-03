import os
import shutil
import unittest
import utils
import translate_single_file as tsf

class TestTranslateSingleFile(unittest.TestCase):
    def setUp(self):
        # Create a temporary pooling directory with dummy files.
        self.pooling_dir = "./temp_pool"
        os.makedirs(os.path.join(self.pooling_dir, "input_pool"), exist_ok=True)
        self.input_file = "test.txt"
        with open(os.path.join(self.pooling_dir, "input_pool", self.input_file), "w") as f:
            f.write("Hello World")
        # Use "dummy" mode so that the dummy translator (text reversal) is used.
        self.model_dir = "dummy"

    def tearDown(self):
        shutil.rmtree(self.pooling_dir)
        # Remove any local copies.
        if os.path.exists(self.input_file):
            os.remove(self.input_file)
        translated = self.input_file + ".translated"
        if os.path.exists(translated):
            os.remove(translated)

    def test_translation(self):
        tsf.translate_single_file(
            translation_type=utils.TypeOfTranslation.en_to_fr,
            pooling_dir=self.pooling_dir,
            model_dir=self.model_dir,
        )
        # Check that the translated file exists in the correct directory.
        translated_file_path = os.path.join(self.pooling_dir, "french_pool", self.input_file)
        self.assertTrue(os.path.exists(translated_file_path))
        with open(translated_file_path, "r") as f:
            content = f.read()
        # The dummy translator reverses the text.
        self.assertEqual(content, "dlroW olleH")

if __name__ == "__main__":
    unittest.main()
