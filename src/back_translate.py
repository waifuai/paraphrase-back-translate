"""
Main entry point for back-translation paraphrasing.
"""

import translate_and_log_multi_file
# No longer need utils here directly for TypeOfTranslation enum
from config import Config # Import Config

def main(config: Config):
    """
    Main entry point for the program.

    Args:
        config: Configuration object containing all parameters.
    """
    # Enum conversion and local_base_dir are handled by Config or passed down

    # Pass the config object directly
    translate_and_log_multi_file.translate_and_log_multi_file(config=config)


if __name__ == "__main__":
    # Default parameters if run directly.
    # Create a default Config object
    default_config = Config(
        cycles=1,
        initial_translation_type_str="en_to_fr",
        pooling_dir="./data/pooling",
        model_dir="./models", # Use "dummy" for testing without models
        log_dir="./logs",
        # local_base_dir defaults to "."
    )
    main(config=default_config)
