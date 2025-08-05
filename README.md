# Back Translate CLI (Gemini API Version)

This project performs back-translation for paraphrase generation using the Google GenAI SDK. It takes text files from an input pool, translates them (e.g., English to French), then translates the result back (e.g., French to English) over a specified number of cycles using a specified Gemini model.

## Files

- [`src/main.py`](src/main.py:1): Command-line interface entry point. Parses arguments and starts the process.
- [`src/back_translate.py`](src/back_translate.py:1): Main logic orchestrating the back-translation cycles.
- [`src/translate_and_log_multi_file.py`](src/translate_and_log_multi_file.py:1): Manages multiple back-translation cycles, alternating translation direction.
- [`src/translate_single_file.py`](src/translate_single_file.py:1): Handles translation of a single file using the Google GenAI SDK.
- [`src/log_single_file.py`](src/log_single_file.py:1): Configures logging and logs cycle completion.
- [`src/update_custom_log.py`](src/update_custom_log.py:1): Helper function to log metrics using standard Python logging.
- [`src/config.py`](src/config.py:1): Defines the `Config` dataclass to hold settings, including API key loading.
- [`src/utils.py`](src/utils.py:1): Basic utility functions (e.g., getting random files).
- [`LICENSE`](LICENSE:1): Project license (MIT-0).
- [`pytest.ini`](pytest.ini:1): Configuration for pytest.
- [`.gitignore`](.gitignore:1): Specifies intentionally untracked files that Git should ignore.

## Model Information

This version uses Google GenAI for translation. You can specify the model name via the command line (default: `gemini-2.5-pro`). Access requires a Gemini API key.

## Installation

It is recommended to use a virtual environment. This project uses `uv` for environment and package management.

1.  Create virtual environment:
    ```bash
    python -m uv venv .venv
    ```
2.  Activate environment:
    ```bash
    # On Windows bash shells like Git Bash
    source .venv/Scripts/activate
    # On Linux/macOS
    # source .venv/bin/activate
    ```
3.  Install tooling into the venv (if needed) and dependencies:
    ```bash
    .venv/Scripts/python.exe -m ensurepip
    .venv/Scripts/python.exe -m pip install uv
    # Runtime only
    .venv/Scripts/python.exe -m uv pip install -r requirements.txt
    # Or for contributors/CI
    .venv/Scripts/python.exe -m uv pip install -r requirements-dev.txt
    ```

## Setup

1.  API Key:
    - Preferred: set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in your environment.
    - Fallback: save the key in a plain text file at `~/.api-gemini`. You can specify a different path using the `--api-key-path` argument.
    - Security: keep this secret and out of version control.

2.  Directory Structure:
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
.venv/Scripts/python.exe -m src.main --cycles 1 --translation-type fr_to_en --pooling-dir ./my_data --log-dir ./my_logs --gemini-model gemini-2.5-pro --api-key-path /path/to/my/gemini.key
```

Arguments:

- `--cycles`: Number of back-translation cycles (default: 1). Each cycle involves one forward and one backward translation (e.g., en->fr then fr->en).
- `--translation-type`: Initial translation direction (`en_to_fr` or `fr_to_en`, default: `en_to_fr`).
- `--pooling-dir`: Directory containing the `input_pool`, `french_pool`, etc. subdirectories (default: `./data/pooling`).
- `--log-dir`: Directory where log files will be created (default: `./logs`).
- `--gemini-model`: Name of the Gemini model to use (default: `gemini-2.5-pro`).
- `--api-key-path`: Path to the file containing your Gemini API key (default: `~/.api-gemini`).

The script will randomly select a file from the appropriate input pool (`input_pool` for `en_to_fr`, `french_pool` for `fr_to_en`), translate it using the Gemini API, move the original to the corresponding `_completed` directory, and place the translated file in the output pool (`french_pool` for `en_to_fr`, `output_pool` for `fr_to_en`). This process repeats, alternating the translation direction for the specified number of cycles. Log messages indicating progress and any errors will be printed to the console and saved in the file specified by `--log-dir` (default: `./logs/backtranslate.log`).

## Dependencies

Two requirement files are provided to balance consumer flexibility and contributor reproducibility:

- Runtime [`requirements.txt`](requirements.txt:1):
  ```
  google-genai~=1.28
  ```
- Development [`requirements-dev.txt`](requirements-dev.txt:1):
  ```
  -r requirements.txt
  pytest==8.3.3
  iniconfig==2.1.0
  packaging==25.0
  pluggy==1.6.0
  colorama==0.4.6
  ```

Install patterns:

```bash
# Runtime only
.venv/Scripts/python.exe -m uv pip install -r requirements.txt
# Development/CI
.venv/Scripts/python.exe -m uv pip install -r requirements-dev.txt
# Run tests
.venv/Scripts/python.exe -m pytest -q
```
