import os
import shutil
import unittest
import utils

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./temp_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "dummy.txt"), "w") as f:
            f.write("dummy")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_is_dir_exist(self):
        self.assertTrue(utils.is_dir_exist(self.test_dir))
        self.assertFalse(utils.is_dir_exist("nonexistent_dir"))

    def test_get_random_file_from_dir(self):
        file = utils.get_random_file_from_dir(self.test_dir)
        self.assertEqual(file, "dummy.txt")

if __name__ == "__main__":
    unittest.main()
