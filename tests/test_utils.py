import os
import shutil
import unittest
import utils

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_temp_utils"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, "dummy.txt")
        with open(self.test_file, "w") as f:
            f.write("dummy")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_is_dir_exist(self):
        self.assertTrue(utils.is_dir_exist(self.test_dir))
        self.assertFalse(utils.is_dir_exist("nonexistent_dir"))

    def test_get_random_file_from_dir(self):
        file = utils.get_random_file_from_dir(self.test_dir)
        self.assertEqual(file, "dummy.txt")

    def test_get_random_file_from_dir_empty(self):
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        with self.assertRaises(RuntimeError):
            utils.get_random_file_from_dir(empty_dir)

    def test_is_files_left_in_dir(self):
        self.assertTrue(utils.is_files_left_in_dir(self.test_dir))
        empty_dir = os.path.join(self.test_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        self.assertFalse(utils.is_files_left_in_dir(empty_dir))
        self.assertFalse(utils.is_files_left_in_dir("nonexistent_dir"))

    def test_is_file_has_size(self):
        self.assertTrue(utils.is_file_has_size(self.test_file, 5))  # Correct size
        self.assertFalse(utils.is_file_has_size(self.test_file, 10))  # Incorrect size
        self.assertFalse(
            utils.is_file_has_size("nonexistent_file.txt", 0)
        )  # Nonexistent file

if __name__ == "__main__":
    unittest.main()
