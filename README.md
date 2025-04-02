# Back Translate CLI (Hugging Face Version)

This project performs back-translation for paraphrase generation using Hugging Face Transformers. It takes text files from an input pool, translates them (e.g., English to French), then translates the result back (e.g., French to English) over a specified number of cycles.

## Files

- **`src/main.py`**: Command-line interface entry point. Parses arguments and starts the process.
- **`src/back_translate.py`**: Main logic orchestrating the back-translation cycles.
- **`src/translate_and_log_multi_file.py`**: Manages multiple back-translation cycles, alternating translation direction.
- **`src/translate_single_file.py`**: Handles translation of a single file using Hugging Face models (`Helsinki-NLP/opus-mt-*`).
- **`src/log_single_file.py`**: Configures logging and logs cycle completion.
- **`src/update_custom_log.py`**: Helper function to log metrics using standard Python logging.
- **`src/config.py`**: Defines the `Config` dataclass to hold settings.
- **`src/utils.py`**: Basic utility functions (e.g., getting random files).
- **`src/tests/`**: Contains the test suite (`unittest`).
- **`plans/`**: Contains planning documents.
- **`LICENSE`**: Project license (MIT-0).
- **`pytest.ini`**: Configuration for pytest.
- **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.

## Model Information

This version uses pre-trained models from the Hugging Face Hub, specifically from the Helsinki-NLP group:
- **English to French:** `Helsinki-NLP/opus-mt-en-fr`
- **French to English:** `Helsinki-NLP/opus-mt-fr-en`

These models will be downloaded automatically on first use if they are not found in the Hugging Face cache directory (usually `~/.cache/huggingface/hub`).

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
    Ensure `pip` and `uv` are available within the environment, then install required packages.
    ```bash
    # Ensure pip (might not be needed depending on uv version)
    python -m ensurepip
    # Install uv inside the venv
    python -m pip install uv
    # Install project dependencies (including PyTorch with CUDA 11.8 support)
    python -m uv pip install transformers torch==2.2.2+cu118 sentencepiece pytest -f https://download.pytorch.org/whl/torch_stable.html
    ```
    *(Adjust the `torch` version and CUDA suffix (`+cu118`) if needed for your specific GPU setup. Check PyTorch website for details.)*

## Directory Structure Setup

Before running, create the necessary directory structure for input/output files:

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
# Example: Run 2 back-translation cycles starting with en->fr
.venv/Scripts/python.exe -m src.main --cycles 2 --translation-type en_to_fr --pooling-dir ./data/pooling --log-dir ./logs
```

**Arguments:**

*   `--cycles`: Number of back-translation cycles (default: 1). Each cycle involves one forward and one backward translation (e.g., en->fr then fr->en).
*   `--translation-type`: Initial translation direction (`en_to_fr` or `fr_to_en`, default: `en_to_fr`).
*   `--pooling-dir`: Directory containing the `input_pool`, `french_pool`, etc. subdirectories (default: `./data/pooling`).
*   `--log-dir`: Directory where log files will be created (default: `./logs`).

The script will randomly select a file from the appropriate input pool (`input_pool` for `en_to_fr`, `french_pool` for `fr_to_en`), translate it, move the original to the corresponding `_completed` directory, and place the translated file in the output pool (`french_pool` for `en_to_fr`, `output_pool` for `fr_to_en`). This process repeats, alternating the translation direction for the specified number of cycles. Log messages indicating progress and any errors will be printed to the console and saved in `./logs/backtranslate.log`.
