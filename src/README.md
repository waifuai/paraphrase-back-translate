# Back-translation Paraphrasing with Hugging Face Transformers

This project implements a back-translation paraphrasing system using the Hugging Face Transformers library and PyTorch. It provides a command-line interface (CLI) to perform back-translation cycles between English and French. The core functionality involves translating text from a source language to a target language and then back to the source language, using pre-trained models from the Hugging Face Hub (`Helsinki-NLP/opus-mt-*`). The system manages input and output files and tracks progress with standard Python logging.

## Project Structure

The `src` directory contains the core Python modules:

-   **`main.py`**: CLI entry point. Parses command-line arguments and initiates the back-translation process.
-   **`back_translate.py`**: Main program logic. Calls `translate_and_log_multi_file` to handle multiple cycles.
-   **`translate_and_log_multi_file.py`**: Manages multiple back-translation cycles, alternating translation direction (English to French, then French to English, etc.).
-   **`translate_single_file.py`**: Handles the translation of a single file using the Hugging Face model. Includes file I/O and interaction with the Transformers library for tokenization and generation.
-   **`log_single_file.py`**: Configures the Python logger and logs the completion of each cycle.
-   **`update_custom_log.py`**: Helper function to log metrics using the standard Python `logging` module.
-   **`config.py`**: Defines the `Config` dataclass holding application settings derived from CLI arguments.
-   **`utils.py`**: Contains basic utility functions (e.g., random file selection).
-   **`tests/`**: Contains the unit tests for the project (located outside `src` in the main project directory).

## Functionality

1.  **Back-translation Cycles:** The system performs back-translation by repeatedly translating text between English and French using specified Hugging Face models. The number of cycles is configurable via the CLI.

2.  **Translation Models:** The project utilizes pre-trained sequence-to-sequence models from the Hugging Face Hub, specifically:
    *   `Helsinki-NLP/opus-mt-en-fr` for English to French.
    *   `Helsinki-NLP/opus-mt-fr-en` for French to English.
    These models are downloaded automatically when the script is run if they are not already present in the local Hugging Face cache.

3.  **File Management:**
    *   Input files (`.txt`) are selected randomly from an input pool directory (`data/pooling/input_pool` for English, `data/pooling/french_pool` for French, relative to the main project directory).
    *   After processing, the original input file is moved to a corresponding "completed" directory (e.g., `data/pooling/input_pool_completed`).
    *   Translated files are written directly to the appropriate output directory (`data/pooling/french_pool` for en->fr, `data/pooling/output_pool` for fr->en), using the same filename as the original input.

4.  **Logging:** The system logs information about the process, including cycle completion and potential errors, using the standard Python `logging` module. Logs are written to `logs/backtranslate.log` (relative to the main project directory).

5.  **CLI:** The command-line interface (`main.py`) allows users to control:
    *   `--cycles`: Number of back-translation cycles (default: 1).
    *   `--translation-type`: Initial translation direction ("en_to_fr" or "fr_to_en", default: "en_to_fr").
    *   `--pooling-dir`: Base directory containing the input/output/completed subdirectories (default: "./data/pooling").
    *   `--log-dir`: Directory for the log file (default: "./logs").

## Setup and Usage

Refer to the main `README.md` in the project root for detailed setup instructions (virtual environment creation, dependency installation using `uv`).

1.  **Directory Structure:** Ensure the required pooling directories exist within the directory specified by `--pooling-dir` (defaults to `./data/pooling`):
    *   `input_pool/` (with initial English `.txt` files)
    *   `french_pool/` (can be initially empty)
    *   `output_pool/` (can be initially empty)
    *   `input_pool_completed/` (created automatically if needed)
    *   `french_pool_completed/` (created automatically if needed)
    The log directory (`./logs` by default) is created automatically.

2.  **Running the script:** Execute `main.py` as a module from the project root directory, using the Python interpreter from your activated virtual environment:

    ```bash
    # Example: Run 3 cycles, starting en->fr, using default dirs
    .venv/Scripts/python.exe -m src.main --cycles 3 --translation-type en_to_fr
    ```

    Adjust `--cycles`, `--translation-type`, `--pooling-dir`, and `--log-dir` as needed.

3.  **Output:** After execution, the final paraphrased text files (after the last fr->en step) will be in the `output_pool` directory. Intermediate French translations will be in the `french_pool`. Processed input files will be moved to the `_completed` directories. Logs will be in `logs/backtranslate.log`.

## Error Handling

-   The script will raise an `OSError` if the required Hugging Face models cannot be downloaded (e.g., due to network issues or invalid model names).
-   A `RuntimeError` is raised by `utils.get_random_file_from_dir` if an input directory is empty when a file is needed.
-   Errors during translation or file moving are logged. Translation errors result in a file containing an error message being written to the output directory.

## Notes

- This README provides an overview specific to the `src` directory modules. See the main project `README.md` for overall project information.
- File paths for pooling and logs are relative to the project root directory where the command is run.
- The script uses `torch` and attempts to use a CUDA GPU if available and correctly configured in the environment. Otherwise, it falls back to CPU.