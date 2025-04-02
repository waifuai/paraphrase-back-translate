#!/usr/bin/env python
"""
CLI entry point for back-translation paraphrasing using Hugging Face Transformers.
"""

import argparse
from back_translate import main
from config import Config # Import the Config class

def parse_args():
    parser = argparse.ArgumentParser(
        description="Back-translation paraphrasing CLI using Hugging Face Transformers."
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
        help="Directory containing input and output files.",
    )
    # Removed --model-dir argument
    # parser.add_argument(
    #     "--model-dir",
    #     type=str,
    #     default="./models",
    #     help=("Directory containing the translation model and vocabulary files. "
    #           "For testing, you may use 'dummy' to trigger a dummy translator."),
    # )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="Directory for logging cycle progress.",
    )
    return parser.parse_args()

def main_cli():
    args = parse_args()
    # Create Config object from parsed arguments
    config = Config(
        cycles=args.cycles,
        initial_translation_type_str=args.translation_type,
        pooling_dir=args.pooling_dir,
        # model_dir=args.model_dir, # Removed
        log_dir=args.log_dir,
        # local_base_dir defaults to "." in Config class
    )
    # Pass the single config object
    main(config=config)

if __name__ == "__main__":
    main_cli()
