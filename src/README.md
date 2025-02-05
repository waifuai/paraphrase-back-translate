# Back-translation Paraphrasing with Trax

This project implements a back-translation paraphrasing system using the Trax deep learning library. It provides a command-line interface (CLI) to perform back-translation cycles between English and French.  The core functionality involves translating text from a source language to a target language and then back to the source language, using a pre-trained Trax Transformer model.  The system manages input and output files, tracks progress with logs, and supports multiple translation cycles.  It includes a dummy translation mode for testing purposes.

## Project Structure

The project is organized into the following files:

-   **`main.py`**:  CLI entry point.  Parses command-line arguments and initiates the back-translation process.
-   **`back_translate.py`**:  Main program logic.  Calls `translate_and_log_multi_file` to handle multiple cycles.
-   **`translate_and_log_multi_file.py`**:  Manages multiple back-translation cycles, alternating translation direction (English to French, then French to English, etc.).
-   **`translate_single_file.py`**:  Handles the translation of a single file using the Trax model (or a dummy translator for testing). Includes file I/O and interaction with Trax's decoding functions.
-   **`log_single_file.py`**:  Updates a custom log (using TensorBoard) to track the progress of back-translation cycles.
-   **`update_custom_log.py`**:  Helper function to write scalar values to a TensorBoard log.
-   **`utils.py`**:  Contains utility functions for file system operations, shell command execution, random file selection, and defining the `TypeOfTranslation` enum.

## Functionality

1.  **Back-translation Cycles:** The system performs back-translation by repeatedly translating text between English and French. The number of cycles is configurable.

2.  **Translation Model:** The project utilizes a pre-trained Trax Transformer model for translation.  The model files (`model_en_fr.pkl.gz` and `model_fr_en.pkl.gz`) and vocabulary files (`vocab_en_fr.subword` and `vocab_fr_en.subword`) are expected to reside in a specified directory.

3.  **Dummy Translation:** For testing purposes, a "dummy" translation mode can be activated by setting the model directory to "dummy". In this mode, the text is simply reversed instead of being translated.

4.  **File Management:**
    -   Input files are selected randomly from an "input pool" directory (`data/pooling/input_pool` for English, `data/pooling/french_pool` for French).
    -   After translation, input files are moved to a "completed" directory (e.g., `data/pooling/input_pool_completed`).
    -   Translated files are placed in the output directory (`data/pooling/french_pool` for English to French, `data/pooling/output_pool` for French to English).
    - The file structure is relative to the project directory.

5.  **Logging:** The system tracks the number of completed back-translation cycles. A counter is stored in `logs/cycle_count.txt`, and a TensorBoard log is updated to visualize progress.

6. **CLI:** The command line interface allows users to control the following.
    -   `--cycles`: Number of back-translation cycles (default: 1).
    -   `--translation-type`: Initial translation direction ("en_to_fr" or "fr_to_en", default: "en_to_fr").
    -   `--pooling-dir`: Directory for input and output files (default: "./data/pooling").
    -   `--model-dir`: Directory for model and vocabulary files (default: "./models"). Use "dummy" for dummy translation mode.
    -   `--log-dir`: Directory for logs (default: "./logs").

## Setup and Usage

1.  **Dependencies:**  This project uses Trax and TensorFlow.  Ensure these libraries are installed.

2.  **Directory Structure:**
    -   Create the following directories:
        -   `data/pooling/input_pool`:  Place initial English text files here.
        -   `data/pooling/french_pool`:  (Initially empty, will contain French translations).
        -   `data/pooling/output_pool`: (Will contain final paraphrased text).
        -   `data/pooling/input_pool_completed`: (Input files moved here after processing.)
        -   `data/pooling/french_pool_completed`: (French files moved here after processing.)
        -   `models`:  Place your Trax model files (`model_en_fr.pkl.gz`, `model_fr_en.pkl.gz`, `vocab_en_fr.subword`, `vocab_fr_en.subword`) here.
        -   `logs`:  (Will contain log files).

3.  **Running the script:**

    ```bash
    python src/main.py --cycles <num_cycles> --translation-type <en_to_fr|fr_to_en> --pooling-dir <pooling_dir> --model-dir <model_dir> --log-dir <log_dir>
    ```

    -   Replace `<num_cycles>` with the desired number of cycles (e.g., 2).
    -   Choose `en_to_fr` or `fr_to_en` for the initial translation direction.
    -   Specify the correct paths for `pooling_dir`, `model_dir`, and `log_dir` if they differ from the defaults.
    - For testing with the dummy translator, use `--model-dir dummy`

    Example:
    ```bash
    python src/main.py --cycles 3 --translation-type en_to_fr --model-dir models
    ```

4.  **Output:**  After execution, the final paraphrased text files will be in the `data/pooling/output_pool` directory.  The `logs` directory will contain the `cycle_count.txt` file and TensorBoard log files.

## Error Handling

-   The script raises a `FileNotFoundError` if the specified model files are not found in the `model_dir`.
-   A `RuntimeError` is raised if the input directory is empty.
-   Shell commands are executed with `check=True`, raising an exception on failure.

## Notes

- This README provides a high-level overview of the project. Refer to the docstrings within the code for more detailed information about individual functions and classes.
- The file structure and default paths are relative, assuming the script is run from the project's root directory.
- This system relies on pre-trained Trax models, which need to be obtained separately.
- The dummy translation mode is useful for verifying the file handling and logging logic without requiring a real translation model.
- The logging mechanism uses TensorFlow's summary writer, allowing visualization of the progress in TensorBoard.