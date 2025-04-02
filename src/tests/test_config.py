# tests/test_config.py
import unittest
import shutil
import os
from config import Config, TypeOfTranslation

class TestConfig(unittest.TestCase):

    def test_config_initialization_en_to_fr(self):
        """Tests basic config initialization for en_to_fr."""
        config = Config(
            cycles=2,
            initial_translation_type_str="en_to_fr",
            pooling_dir="./test_pool",
            log_dir="./test_log",
            local_base_dir="./base"
        )
        self.assertEqual(config.cycles, 2)
        self.assertEqual(config.initial_translation_type_str, "en_to_fr")
        self.assertEqual(config.initial_translation_type, TypeOfTranslation.en_to_fr)
        self.assertEqual(config.pooling_dir, "./test_pool")
        self.assertEqual(config.log_dir, "./test_log")
        self.assertEqual(config.local_base_dir, "./base")
        # Assert model_dir and use_dummy_model are gone
        self.assertFalse(hasattr(config, 'model_dir'))
        self.assertFalse(hasattr(config, 'use_dummy_model'))

    def test_config_initialization_fr_to_en(self):
        """Tests basic config initialization for fr_to_en."""
        config = Config(
            cycles=1,
            initial_translation_type_str="fr_to_en",
            pooling_dir="pool",
            log_dir="log"
            # Use default local_base_dir
        )
        self.assertEqual(config.cycles, 1)
        self.assertEqual(config.initial_translation_type_str, "fr_to_en")
        self.assertEqual(config.initial_translation_type, TypeOfTranslation.fr_to_en)
        self.assertEqual(config.pooling_dir, "pool")
        self.assertEqual(config.log_dir, "log")
        self.assertEqual(config.local_base_dir, ".") # Check default

    def test_invalid_translation_type(self):
        """Tests that an invalid translation type raises ValueError."""
        with self.assertRaises(ValueError):
            Config(
                cycles=1,
                initial_translation_type_str="es_to_en", # Invalid type
                pooling_dir="pool",
                log_dir="log"
            )

    def test_get_hf_model_name(self):
        """Tests the HF model name retrieval."""
        config_en = Config(cycles=1, initial_translation_type_str="en_to_fr", pooling_dir="p", log_dir="l")
        config_fr = Config(cycles=1, initial_translation_type_str="fr_to_en", pooling_dir="p", log_dir="l")

        self.assertEqual(config_en.get_hf_model_name(TypeOfTranslation.en_to_fr), "Helsinki-NLP/opus-mt-en-fr")
        self.assertEqual(config_en.get_hf_model_name(TypeOfTranslation.fr_to_en), "Helsinki-NLP/opus-mt-fr-en")
        self.assertEqual(config_fr.get_hf_model_name(TypeOfTranslation.en_to_fr), "Helsinki-NLP/opus-mt-en-fr")
        self.assertEqual(config_fr.get_hf_model_name(TypeOfTranslation.fr_to_en), "Helsinki-NLP/opus-mt-fr-en")

    def test_path_generation(self):
        """Tests the various path generation methods."""
        pooling = "./data/pools"
        logs = "run_logs"
        base = "/tmp/base"
        config = Config(
            cycles=1, initial_translation_type_str="en_to_fr",
            pooling_dir=pooling, log_dir=logs, local_base_dir=base
        )

        # Expected paths (using os.path.join for platform compatibility)
        exp_input_en = os.path.join(pooling, "input_pool")
        exp_input_fr = os.path.join(pooling, "french_pool")
        exp_output_en = os.path.join(pooling, "output_pool")
        exp_output_fr = os.path.join(pooling, "french_pool")
        exp_completed_en = os.path.join(pooling, "input_pool_completed")
        exp_completed_fr = os.path.join(pooling, "french_pool_completed")
        exp_log_dir = os.path.join(base, logs)
        exp_counter_file = os.path.join(base, logs, "cycle_count.txt") # Still exists, though file itself removed from log_single_file

        self.assertEqual(config.get_input_dir(TypeOfTranslation.en_to_fr), exp_input_en)
        self.assertEqual(config.get_input_dir(TypeOfTranslation.fr_to_en), exp_input_fr)
        self.assertEqual(config.get_output_dir(TypeOfTranslation.en_to_fr), exp_output_fr)
        self.assertEqual(config.get_output_dir(TypeOfTranslation.fr_to_en), exp_output_en)
        self.assertEqual(config.get_completed_dir(TypeOfTranslation.en_to_fr), exp_completed_en)
        self.assertEqual(config.get_completed_dir(TypeOfTranslation.fr_to_en), exp_completed_fr)
        self.assertEqual(config.local_log_dir_path, exp_log_dir)
        self.assertEqual(config.cycle_counter_filepath, exp_counter_file)

        # Ensure log directory is created by property access
        if os.path.exists(exp_log_dir): # Clean up if exists from previous runs
            shutil.rmtree(exp_log_dir)
        self.assertFalse(os.path.exists(exp_log_dir))
        _ = config.local_log_dir_path # Access property
        self.assertTrue(os.path.exists(exp_log_dir))
        _ = config.cycle_counter_filepath # Access property
        self.assertTrue(os.path.exists(exp_log_dir)) # Should still exist
        # Clean up created directory
        shutil.rmtree(base)


if __name__ == '__main__':
    unittest.main()