## Gutenberg Download Sub-Project

This directory contains the `gutenberg_download` sub-project, a dedicated module for interacting with Project Gutenberg data. It provides functionality to either download book texts directly from the Gutendex API (online mode) or process existing local `.txt.gz` files from a Project Gutenberg mirror (local mode). All processed books are cleaned of boilerplate and saved as structured JSON files for further use in the main project.

## Table of Contents

-   [Features](#features)
-   [Installation](#installation)
-   [Usage](#usage)
    -   [Online Download Mode](#online-download-mode)
    -   [Local Processing Mode](#local-processing-mode)
    -   [Configuration for Search Parameters](#configuration-for-search-parameters)
-   [Output Format](#output-format)
-   [Project Structure](#project-structure)
-   [Contributing](#contributing)
-   [License](#license)

## Features

* **Flexible Data Source:** Download books directly from the Gutendex API or process locally stored Gutenberg files.
* **Intelligent Text Cleaning:** Automatically removes Project Gutenberg headers, footers, and other boilerplate text, preserving meaningful paragraph breaks.
* **Metadata Integration:** Fetches and stores relevant book metadata (title, authors, Gutenberg ID) alongside the cleaned text.
* **Structured Output:** Saves processed book data in a consistent JSON format, ready for downstream NLP tasks.
* **Configurable Search:** Use a YAML configuration file to define search parameters for the Gutendex API (e.g., `topic`, `languages`, `author`).
* **Customizable Gutendex URL:** Option to specify a different Gutendex API endpoint.

## Installation



## Usage

The `gutenberg_download` module is primarily run via its `main.py` script. You can execute it from your project's root directory.

```bash
python gutenberg_download/main.py --help
````

This will display the available command-line arguments:

```
usage: main.py [-h] --mode {online,local} [--output_dir OUTPUT_DIR] [--limit LIMIT] [--metadata_url METADATA_URL] [--search_config SEARCH_CONFIG] [--local_data_dir LOCAL_DATA_DIR]

Download and process books from Project Gutenberg (online or local).

options:
  -h, --help            show this help message and exit
  --mode {online,local}
                        Choose download mode: 'online' for API-based download, 'local' for processing local .txt.gz files.
  --output_dir OUTPUT_DIR
                        Directory to save the processed JSON book files.
  --limit LIMIT         Maximum number of books to process/download. (Applies to both modes).
  --metadata_url METADATA_URL
                        Base URL for the Gutendex API. (Applies to both online and local modes for metadata retrieval).
  --search_config SEARCH_CONFIG
                        Path to the YAML configuration file for online search parameters.
  --local_data_dir LOCAL_DATA_DIR
                        Path to the directory containing local Project Gutenberg .txt.gz files. Required for 'local' mode.
```

### Gutendex API
Gutendex is a modern API for Project Gutenberg, providing a simple and efficient way to access book metadata and content. It allows you to search for books based on various parameters like author, language, topic, and more.
By default, the `gutenberg_download` module uses the Gutendex API to fetch metadata and book content. You can specify a custom Gutendex URL if needed.
To install a local copy of the Gutendex API, refer to the [Gutendex installation guide](https://github.com/garethbjohnson/gutendex)

### Online Download Mode

To download books directly from Gutenberg website:

```bash
python main.py --mode online  --output_dir downloaded_books --limit 20 --search_config config/search_config.yaml 
```

  - `--mode online`: Specifies the online download mode.
  - `--output_dir`: The directory where the processed JSON files will be saved. (Default: `processed_books`)
  - `--limit`: The maximum number of books to download. (Default: 10)
  - `--search_config`: Path to your YAML file containing Gutendex API search parameters. (Default: `search_config.yaml`)
  - `--metadata_url`: (Optional) Specify a custom Gutendex API URL. (Default: `https://gutendex.com/`)

### Local Processing Mode

To process `.txt.gz` files from a local Project Gutenberg mirror (e.g., if you have downloaded the entire dataset):
The archive of Project Gutenberg books can be downloaded from [Project Gutenberg's official site](https://www.gutenberg.org/ebooks/offline_catalogs.html), or you can use a mirror that provides the `.txt.gz` files.
```bash
python gutenberg_download/main.py --mode local --local_data_dir /path/to/your/gutenberg/mirror/data --output_dir processed_books_local --limit 50 
```

  - `--mode local`: Specifies the local processing mode.
  - `--local_data_dir`: **Required** path to the directory containing the decompressed Gutenberg `.txt.gz` files. These are typically organized in subdirectories by ID (e.g., `.../data/gutenberg/books/1/1.txt.gz`, `.../data/gutenberg/books/2/2.txt.gz`).
  - `--output_dir`: The directory where the processed JSON files will be saved. (Default: `processed_books`)
  - `--limit`: The maximum number of books to process. (Default: 10)
  - `--metadata_url`: (Optional) Even in local mode, metadata (title, authors, etc.) is retrieved from Gutendex. You can specify a custom URL here. (Default: `https://gutendex.com/`)
    *Note: The `search_config` parameter is still used in local mode to filter the metadata retrieved from Gutendex, allowing you to select which local files to process based on metadata criteria.*

### Configuration for Search Parameters

Create a `search_config.yaml` file (or whatever you specify with `--search_config`) in the `gutenberg_download/` directory or your project root. This file uses YAML syntax to define parameters for the Gutendex API.

**Example `config/search_config.yaml`:**

```yaml
# Search for books with 'adventure' in the topic or title, in English,
# and by authors whose last name starts with 'Twain'.
search: adventure
languages: en
# You can use other Gutendex parameters like:
# topic: fantasy
# author_year_start: 1800
# author_year_end: 1900
# author: Twain
```

Refer to the [Gutendex API documentation](https://gutendex.com/) for a full list of available search parameters.

## Output Format

Each processed book will be saved as a JSON file in the specified `--output_dir`. The structure of each JSON file follows the `ProcessorInput` schema:

```json
{
  "text": "The cleaned and processed text of the book, with boilerplate removed and paragraphs normalized.",
  "title": "The Title of the Book",
  "authors": [
    "Author One",
    "Author Two"
  ],
  "gutenberg_id": 12345
}
```

## Project Structure

```
books_processing/
├── common/
│   ├── __init__.py
│   └── load_config.py  
├── gutenberg_download/
│   ├── main.py # Main to download books from gutenberg project
│   ├── gutenberg_download/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── gutenberg_downloader.py  # Contains core logic for downloading/processing
│   │   │   └── metadata_schema.py       # Pydantic models for Gutendex API responses            
└── ... (other project directories/files)
```
