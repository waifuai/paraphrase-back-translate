# Back Translate CLI

This project performs back-translation for paraphrase generation using Trax.

## Files

- **`cli.py`**: Command-line interface entry point.
- **`back_translate.py`**: Main logic for back-translation.
- **`log_single_file.py`**: Updates the log after each cycle.
- **`translate_and_log_multi_file.py`**: Manages multiple back-translation cycles and logging.
- **`translate_single_file.py`**: Handles translation of a single file using Trax.
- **`update_custom_log.py`**: Updates a TensorBoard log file.
- **`utils.py`**: Utility functions.
- **`tests/`**: Contains the test suite.

## Model and Vocabulary Files

Place your pre-trained translation models and vocabulary files in the directory specified by `--model-dir`. For example:
- For English-to-French translation:
  - Model file: `model_en_fr.pkl.gz`
  - Vocabulary file: `vocab_en_fr.subword`
- For French-to-English translation:
  - Model file: `model_fr_en.pkl.gz`
  - Vocabulary file: `vocab_fr_en.subword`

For testing, you may run with `--model-dir dummy` to use a dummy translator (which reverses the input text).

## Installation

Install the dependencies via pip:

```bash
pip install trax tensorflow
```

You can also install this package locally using the provided `setup.py`.

## Usage

Run the CLI as follows:

```bash
back-translate --cycles 2 --translation-type en_to_fr --pooling-dir ./data/pooling --model-dir ./models --log-dir ./logs
```
