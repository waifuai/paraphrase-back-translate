# Test Suite for Back-Translation Project

This README describes the test suite for a back-translation project.  The tests cover various aspects of the application, including argument parsing, file handling, translation (using a dummy model), logging, and utility functions.  The tests use `unittest` and `unittest.mock` extensively for mocking external dependencies and filesystem interactions.

## Test Files

The test suite is organized into several files, each focusing on a specific part of the application:

*   **`tests/test_back_translate.py`**: Tests the main entry point of the back-translation process (`back_translate.main`). It checks the correct handling of arguments and calls to the `translate_and_log_multi_file` function.

*   **`tests/test_log_single_file.py`**: Tests the functionality for logging a single cycle of the back-translation process (`log_single_file.log_single_cycle`).  It verifies the creation of log directories, incrementing cycle counts in a file, and calls to the custom logging function. It also ensures that the logging directory is created as expected.

*   **`tests/test_main.py`**: Tests the command-line interface (`main.main_cli`).  It simulates command-line arguments using `sys.argv` and verifies that the `main` function is called with the expected parameters, including default values.

*   **`tests/test_translate_and_log_multi_file.py`**: Tests the `translate_and_log_multi_file` function, which orchestrates multiple translation cycles. It verifies that the `translate_and_log_single_cycle` function is called the correct number of times and with the appropriate translation types (e.g., English to French, then French to English).  It also tests the case where the number of cycles is zero.

*   **`tests/test_translate.py`**: Tests the core translation logic in `translate_single_file.translate_single_file`. This is the most comprehensive test file, covering:
    *   Successful dummy translation (English to French and French to English).
    *   Correct file movement between input, output, and completed directories.
    *   Error handling when a model directory is missing.
    *   Handling of empty input files.
    *   Translation of varied input text (including punctuation and numbers).
    *   Local file creation to save the input text file.

*   **`tests/test_update_custom_log.py`**: Tests the custom logging function (`update_custom_log.update_custom_log`) that integrates with TensorFlow's summary writer.  It mocks the TensorFlow summary writing functions to ensure they are called correctly with the specified parameters.

*   **`tests/test_utils.py`**: Tests various utility functions in the `utils` module.  It covers:
    *   Checking if a directory exists.
    *   Retrieving a random file from a directory.
    *   Handling empty directories when trying to get a random file (raising an error).
    *   Checking if files are left in a directory.
    *   Checking if a file has a specific size.

## Testing Strategy

The tests primarily use the following strategies:

*   **Mocking:** The `unittest.mock` library (specifically, `patch` and `MagicMock`) is used extensively to replace external dependencies with mock objects. This allows isolating the units under test and controlling their behavior.  Mocking is used for:
    *   External function calls (e.g., `translate_and_log_multi_file`, `update_custom_log`).
    *   TensorFlow summary writing.
    * The `main` function for command-line interaction.
    *   File system interactions (partially, using temporary directories).

*   **Temporary Directories:** The `setUp` and `tearDown` methods in several test classes create and remove temporary directories (`test_temp_...`). This ensures that tests do not interfere with each other or with the real filesystem.  It also provides a clean environment for each test run.

*   **Assertions:**  A variety of assertion methods from `unittest.TestCase` are used to verify the expected behavior, including:
    *   `assertEqual`:  Checks for equality.
    *   `assertTrue` / `assertFalse`: Checks for boolean values.
    *   `assertRaises`:  Checks that a specific exception is raised.
    *   `assert_called_once_with`, `assert_any_call`, `assert_not_called`:  Checks how mock objects were called.
    *   `os.path.exists`: Checks if files or directories exist.

*   **Dummy Translation Model:** The `translate_single_file` tests use a "dummy" translation model.  Instead of performing actual translation, the dummy model reverses the input string.  This simplifies testing by avoiding the need for a real, complex translation model while still verifying file handling and the translation workflow.

* **Testing edge cases**: The tests ensure that error cases and boundaries are tested. For example, the code tests that:
    * When a model doesn't exist, it raises a `FileNotFoundError`.
    * When a directory from which to get random files is empty, it raises a `RuntimeError`.
    * When the number of cycles is set to zero, it does not execute the translate and log cycle.

## Running the Tests

To run the tests, you can typically use a command like:

```bash
python -m unittest discover tests
```

This command will discover and run all test files in the `tests` directory.  You may need to adapt this command depending on your project's setup and testing framework.