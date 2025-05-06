"""
Main entry point for back-translation paraphrasing using the Gemini API.
"""
import logging
import translate_and_log_multi_file
from config import Config # Import Config

# Configure logging for this module
logger = logging.getLogger(__name__)

def main(config: Config):
    """
    Main entry point for the program.

    Args:
        config: Configuration object containing all parameters (including API key).
    """
    logger.info("Starting back-translation main function.")
    # Pass the config object directly
    translate_and_log_multi_file.translate_and_log_multi_file(config=config)
    logger.info("Finished back-translation main function.")


# The __main__ block is primarily for direct execution testing/debugging.
# It's generally better to run via the main_cli entry point.
# Keeping it here but commenting out the direct call to main().
# If needed for testing, uncomment and ensure a valid config can be created.
# if __name__ == "__main__":
#     # Example: Create a default Config object for direct testing
#     # Requires a ~/.api-gemini file or setting the api_key_path correctly.
#     try:
#         default_config = Config(
#             cycles=1,
#             initial_translation_type_str="en_to_fr",
#             pooling_dir="./data/pooling",
#             log_dir="./logs",
#             # api_key_path="~/.api-gemini" # Default path
#             # gemini_model_name="gemini-2.5-pro-preview-05-06" # Default model
#         )
#         # Setup basic logging if run directly
#         logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#         main(config=default_config)
#     except (FileNotFoundError, ValueError) as e:
#         print(f"Error creating default config for direct execution: {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred during direct execution: {e}")
