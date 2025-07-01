# Cuban Energy Report Extractor

This project provides a Python script to extract structured daily energy report data from Telegram chat exports, specifically from the Cuban Electric Company (Empresa Eléctrica de La Habana) channel. It processes the raw JSON export, identifies daily reports, extracts key energy metrics, and saves them into a clean JSON file.

## Setup

1.  **Install `uv`**: follow the instructions on the `uv` documentation.

2.  **Install Dependencies**: Navigate to the project root directory and install the required dependencies:
    ```bash
    uv sync
    ```

## Usage

1.  **Export Telegram Data**:
    *   Open the Telegram Desktop application.
    *   Go to the channel: [Empresa Eléctrica de La Habana](https://t.me/EmpresaElectricaDeLaHabana).
    *   Click on the channel name at the top to open its profile.
    *   Click on the three dots (`...`) menu (usually in the top right corner).
    *   Select "Export chat history".
    *   Choose "JSON" as the format and select the messages you want to export (e.g., "From the beginning" or a specific date range).
    *   Click "Export".

2.  **Place the Exported File**:
    *   After exporting, you will get a `result.json` file (and potentially other files/folders).
    *   Create a folder named `raw` in the root directory of this project if it doesn't already exist.
    *   Copy the `result.json` file into the `raw` folder.
        ```
        your-project-root/
        ├── raw/
        │   └── result.json
        ├── main.py
        ├── pyproject.toml
        ├── uv.lock
        └── README.md
        ```

3.  **Run the Extractor**:
    *   From the project root directory, execute the script using `uv`:
        ```bash
        uv run main.py
        ```
    *   The script will process the `raw/result.json` file and save the extracted data to `data.json` in the project root.
