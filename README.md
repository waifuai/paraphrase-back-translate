# Back Translate CLI (Gemini API Version)

This project performs back-translation for paraphrase generation using the Google Gemini API. It takes text files from an input pool, translates them (e.g., English to French), then translates the result back (e.g., French to English) over a specified number of cycles using a specified Gemini model.

## Files

- **`src/main.py`**: Command-line interface entry point. Parses arguments and starts the process.
- **`src/back_translate.py`**: Main logic orchestrating the back-translation cycles.
- **`src/translate_and_log_multi_file.py`**: Manages multiple back-translation cycles, alternating translation direction.
- **`src/translate_single_file.py`**: Handles translation of a single file using the Gemini API.
- **`src/log_single_file.py`**: Configures logging and logs cycle completion.
- **`src/update_custom_log.py`**: Helper function to log metrics using standard Python logging.
- **`src/config.py`**: Defines the `Config` dataclass to hold settings, including API key loading.
- **`src/utils.py`**: Basic utility functions (e.g., getting random files).
- **`LICENSE`**: Project license (MIT-0).
- **`pytest.ini`**: Configuration for pytest.
- **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.

## Model Information

This version uses the Google Gemini API for translation. You can specify the model name via the command line (default: `gemini-2.5-flash-preview-04-17`). Access requires a Gemini API key.

## Installation

It is recommended to use a virtual environment. This project uses `uv` for environment and package management.

1.  **Create virtual environment:**
    ```bash
    python -m uv venv .venv
    ```
2.  **Activate environment:**
    ```bash
    # On Windows (Git Bash or similar)
    source .venv/Scripts/activate
    # On Linux/macOS
    # source .venv/bin/activate
    ```
3.  **Install dependencies:**
    Ensure `pip` and `uv` are available within the environment (see user instructions if needed), then install required packages.
    ```bash
    # Ensure pip (might not be needed depending on uv version)
    # .venv/Scripts/python.exe -m ensurepip
    # Install uv inside the venv (recommended)
    # .venv/Scripts/python.exe -m pip install uv
    # Install project dependencies
    .venv/Scripts/python.exe -m uv pip install google-generativeai pytest
    ```
    *(Note: `torch` and `transformers` are no longer required for this version).*

## Setup

1.  **API Key:**
    *   Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Save the key in a plain text file. By default, the script looks for `~/.api-gemini`. You can specify a different path using the `--api-key-path` argument.
    *   **Security:** Ensure this file is kept secure and is included in your `.gitignore` if you are using version control.

2.  **Directory Structure:**
    Before running, create the necessary directory structure for input/output files (relative to where you run the command):
    ```
    ./data/pooling/
    ├── input_pool/             # Place initial English .txt files here
    ├── french_pool/            # Initially empty, will hold en->fr results
    ├── output_pool/            # Initially empty, will hold fr->en results (final paraphrases)
    ├── input_pool_completed/   # Processed English files moved here
    └── french_pool_completed/  # Processed French files moved here
    ./logs/                     # Directory for log files (created automatically)
    ```

## Usage

Run the CLI from the project root directory using the Python interpreter from the virtual environment:

```bash
# Example: Run 2 back-translation cycles starting with en->fr, using defaults
.venv/Scripts/python.exe -m src.main --cycles 2 --translation-type en_to_fr

# Example: Run 1 cycle, fr->en, specifying directories and model
.venv/Scripts/python.exe -m src.main --cycles 1 --translation-type fr_to_en --pooling-dir ./my_data --log-dir ./my_logs --gemini-model gemini-pro --api-key-path /path/to/my/gemini.key
```

**Arguments:**

*   `--cycles`: Number of back-translation cycles (default: 1). Each cycle involves one forward and one backward translation (e.g., en->fr then fr->en).
*   `--translation-type`: Initial translation direction (`en_to_fr` or `fr_to_en`, default: `en_to_fr`).
*   `--pooling-dir`: Directory containing the `input_pool`, `french_pool`, etc. subdirectories (default: `./data/pooling`).
*   `--log-dir`: Directory where log files will be created (default: `./logs`).
*   `--gemini-model`: Name of the Gemini model to use (default: `gemini-2.5-flash-preview-04-17`).
*   `--api-key-path`: Path to the file containing your Gemini API key (default: `~/.api-gemini`).

The script will randomly select a file from the appropriate input pool (`input_pool` for `en_to_fr`, `french_pool` for `fr_to_en`), translate it using the Gemini API, move the original to the corresponding `_completed` directory, and place the translated file in the output pool (`french_pool` for `en_to_fr`, `output_pool` for `fr_to_en`). This process repeats, alternating the translation direction for the specified number of cycles. Log messages indicating progress and any errors will be printed to the console and saved in the file specified by `--log-dir` (default: `./logs/backtranslate.log`).
