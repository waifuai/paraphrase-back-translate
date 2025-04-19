#!/usr/bin/env python
"""
CLI entry point for back-translation paraphrasing using the Gemini API.
"""

import argparse
import logging
from back_translate import main
from config import Config # Import the Config class
from log_single_file import setup_logging # Import setup_logging

# Configure basic logging for the main script entry point
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Back-translation paraphrasing CLI using the Gemini API."
    )
    parser.add_argument(
        "--cycles", type=int, default=1, help="Number of back-translation cycles."
    )
    parser.add_argument(
        "--translation-type",
        choices=["en_to_fr", "fr_to_en"],
        default="en_to_fr",
        help="Initial translation direction.",
    )
    parser.add_argument(
        "--pooling-dir",
        type=str,
        default="./data/pooling",
        help="Directory containing input, output, and completed subdirectories.",
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="Directory for logging cycle progress.",
    )
    parser.add_argument(
        "--gemini-model",
        type=str,
        default="gemini-2.5-flash-preview-04-17", # Default from Config
        help="Name of the Gemini model to use for translation.",
    )
    parser.add_argument(
        "--api-key-path",
        type=str,
        default="~/.api-gemini", # Default from Config
        help="Path to the file containing the Gemini API key.",
    )
    return parser.parse_args()

def main_cli():
    args = parse_args()
    try:
        # Create Config object from parsed arguments
        config = Config(
            cycles=args.cycles,
            initial_translation_type_str=args.translation_type,
            pooling_dir=args.pooling_dir,
            log_dir=args.log_dir,
            gemini_model_name=args.gemini_model,
            api_key_path=args.api_key_path,
            # local_base_dir defaults to "." in Config class
        )

        # Setup logging using the path from the config
        # Note: log_single_file also calls setup_logging, but calling it here
        # ensures logs related to config loading or early errors are captured.
        # The _logger_configured flag in log_single_file prevents duplicate handlers.
        setup_logging(config.log_filepath)

        logger.info("Configuration loaded successfully. Starting back-translation process.")
        # Pass the single config object
        main(config=config)
        logger.info("Back-translation process completed.")

    except FileNotFoundError as e:
        logger.error(f"Configuration Error: {e}")
        print(f"Error: {e}") # Also print to console for visibility
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        print(f"Error: {e}") # Also print to console
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}") # Log full traceback
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main_cli()
