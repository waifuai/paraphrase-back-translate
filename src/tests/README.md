# Test Suite for Back-Translation Project (Hugging Face Version)

This README describes the test suite for the back-translation project, updated after migrating from Trax to Hugging Face Transformers. The tests cover argument parsing, configuration, file handling, translation (using mocked Hugging Face components), logging, and utility functions. The tests use `unittest` and `unittest.mock` extensively for mocking external dependencies and filesystem interactions.

## Test Files

The test suite is organized into several files, each focusing on a specific part of the application:

*   **`tests/test_back_translate.py`**: Tests the main entry point (`back_translate.main`), checking the correct handling of arguments (via the `Config` object) and calls to the `translate_and_log_multi_file` function.
*   **`tests/test_config.py`**: Tests the `Config` dataclass, verifying initialization, derived properties (like `initial_translation_type`), path generation methods, and the new `get_hf_model_name` method.
*   **`tests/test_log_single_file.py`**: Tests the functionality for logging a single cycle (`log_single_file.log_single_cycle`). It verifies the configuration of the standard Python logger, calls to the custom logging function (`update_custom_log`), and checks log file content. It no longer tests the old cycle counter file.
*   **`tests/test_main.py`**: Tests the command-line interface (`main.main_cli`). It simulates command-line arguments and verifies that the `back_translate.main` function is called with a correctly populated `Config` object, reflecting the removal of the `--model-dir` argument.
*   **`tests/test_translate_and_log_multi_file.py`**: Tests the `translate_and_log_multi_file` function, which orchestrates multiple translation cycles. It verifies that `translate_and_log_single_cycle` is called the correct number of times with the appropriate translation types and `Config` object.
*   **`tests/test_translate.py`**: Tests the core translation logic in `translate_single_file.translate_single_file`. This is the most comprehensive test file, now covering:
    *   Successful translation using mocked Hugging Face `AutoModelForSeq2SeqLM` and `AutoTokenizer`.
    *   Correct file movement (input file to completed directory, translated file written directly to output directory).
    *   Error handling during model loading (e.g., `OSError`).
    *   Handling of empty input files (should result in an empty output file).
    *   Error handling during the translation generation step.
    *   Verification that local file copying is no longer performed.
*   **`tests/test_update_custom_log.py`**: Tests the custom logging function (`update_custom_log.update_custom_log`) which now uses the standard Python `logging` module. It mocks the logger to ensure `logger.info` is called with the correctly formatted message.
*   **`tests/test_utils.py`**: Tests various utility functions in the `utils` module (largely unchanged, covering directory/file existence checks, random file retrieval, and error handling for empty directories).

## Testing Strategy

The tests primarily use the following strategies:

*   **Mocking:** `unittest.mock` (`patch`, `MagicMock`) is used extensively to replace external dependencies:
    *   Hugging Face `transformers` classes (`AutoModelForSeq2SeqLM`, `AutoTokenizer`).
    *   `torch.device` to force CPU usage for consistency.
    *   Standard Python `logging` components (`FileHandler`, logger instances).
    *   Internal function calls between modules (e.g., `translate_and_log_multi_file`, `update_custom_log`, `utils.get_random_file_from_dir`).
    *   `sys.argv` for CLI testing.
*   **Temporary Directories:** `setUp` and `tearDown` methods create and remove temporary directories (`test_temp_...`) for filesystem isolation during tests.
*   **Assertions:** `unittest.TestCase` assertions verify expected behavior:
    *   Equality (`assertEqual`), boolean values (`assertTrue`/`assertFalse`), exceptions (`assertRaises`).
    *   Mock call verification (`assert_called_once_with`, `assert_any_call`, `assert_not_called`).
    *   Filesystem checks (`os.path.exists`).
    *   Log file content checks.
*   **Mocked Translation:** The `translate_single_file` tests use mocked Hugging Face models and tokenizers that return predefined outputs, avoiding the need for actual model downloads or GPU execution during testing while still verifying the translation workflow and file handling.
*   **Edge Case Testing:** Tests cover scenarios like empty input files, model loading errors, and translation errors.

## Running the Tests

Ensure you have activated the project's virtual environment (`.venv`) where `pytest` is installed. Run the tests from the project's root directory:

```bash
.venv/Scripts/python.exe -m pytest
```

This command will discover and run all test files in the `tests` directory.