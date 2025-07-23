# Gutenberg Book Ingestion and Processing Suite

This project provides a comprehensive suite of Python tools designed to download, clean, and perform deep semantic analysis on books from the Project Gutenberg corpus. Using Large Language Models (LLMs), it generates abstractive summaries and extracts key themes for each book, producing structured JSON files ready for use in downstream applications like recommendation systems.

This suite is composed of two main modules:

  * **Gutenberg Downloader**: For acquiring and cleaning the book data.
  * **Text Processor**: For analyzing the cleaned text using LLMs.
The project contains two scripts: one for downloading and cleaning books from Project Gutenberg (`download_books.py`), and another for processing the cleaned text to generate summaries and themes using LLMs (`process_books.py`).

## How It Works

The data pipeline operates in a sequential process to transform raw book text into structured, semantically rich data:

1.  **Acquisition**: The `Gutenberg Downloader` module fetches book metadata from the Gutendex API. It can download the raw text files directly from the web or process them from a local mirror.
2.  **Cleaning**: The raw text is rigorously cleaned to remove standard Project Gutenberg headers, footers, and other boilerplate content. Line breaks and whitespace are normalized to create a clean, continuous text body for each book. The output is a structured JSON file containing the cleaned text and metadata.
3.  **Chunking**: To handle the large size of books, the `Text Processor` first divides the cleaned text into smaller, fixed-size chunks. This ensures the text fits within the context window of the LLM.
4.  **Hierarchical Summarization**: The system employs a multi-step summarization strategy:
      * First, an LLM generates a summary for each individual chunk.
      * If the combined summaries of these chunks exceed the LLM's context window, they are further summarized into intermediate summaries.
      * Next, all intermediate summaries are combined and fed back to the LLM to generate a single, coherent, and comprehensive final summary of the entire book.
5.  **Theme Extraction**: During the final summarization step, the LLM is also prompted to identify and list the primary themes of the book.
6.  **Structured Output**: The final output is saved as a new JSON file, containing the book's original metadata along with the newly generated summary and themes.

## Features

  * **Flexible data acquisition** : 
    * Download books metadata directly via the Gutendex API by using search term, filtering topics, authors, languages and so on
    * Download raw text files from Project Gutenberg or process local `.txt.gz` files.
  * **Automated text cleaning**: Intelligently removes Project Gutenberg boilerplate to isolate the literary content.
  * **Advanced LLM analysis**:
      * Performs **hierarchical summarization** to effectively handle book-length texts.
      * Extracts a list of **key themes** for deep semantic understanding.
  * **Multi-LLM Support**: Built-in support for both the **Google Gemini API** and locally-hosted models via **Ollama**.
  * **Structured I/O**: Utilizes Pydantic models to ensure validated, consistent JSON data formats for both input and output.
  * **Highly configurable**: Allows for customization of search parameters for downloading and the prompts used for LLM analysis via YAML files.
  * **Easy to add new models**: The architecture is designed to easily integrate additional LLMs or processing steps as needed.

## Tech Stack

  * **Language**: Python 3.10+
  * **Text Processing**: NLTK (for sentence tokenization)
  * **LLM Services**: Google Gemini API, Ollama
  * **Data Validation**: Pydantic

-----

## Installation

1.  **Clone the repository and install dependencies:**

    ```bash
    git clone https://github.com/Sainane/books_processing.git
    cd books_processing
    pip install -r requirements.txt
    ```

2.  **Download NLTK data:**
    The chunking process relies on NLTK's sentence tokenizer. Download the required data by running:

    ```bash
    python -m nltk.downloader punkt
    ```

## Usage

The process is divided into two main steps: downloading the books and then processing them.

### Step 1: Downloading Books

Use the `download_books.py` script to fetch metadata and text content and clean books.
The metatadata is fetched from the Gutendex API, and can be filtered by various parameters such as language, search term, and topics.
It's also possible to host your own Gutendex instance by specifying the `--gutendex_url` parameter. (See the [Gutendex documentation](https://github.com/garethbjohnson/gutendex) for more details on the API.)
The script can operate in two modes: online (to download books from Project Gutenberg) or local (to process existing `.txt.gz` files).
The output will be a set of cleaned JSON files containing the book text and metadata.
The downloader use a search configuration file to filter the books to download. The search configuration file is a YAML file that specifies the search parameters for the books to download, such as language, search term, and so on.

To see detail of needed parameters, run the script with `--help`:

```bash
python download_books.py --help
```
#### Online mode
To download books online you can use the following command. This will download books metadata from the Gutendex API, then fetch the raw text files from Project Gutenberg, clean them, and save them as JSON files in the specified output directory.

#### Example
```bash
The downloaded books will be cleaned and saved as JSON files, ready for processing in the next step.
```bash
python download_books.py --mode online --output_dir ./books_to_process --limit 1
```


#### Local mode
The local mode is used to process existing `.txt.gz` files. This is useful if you have a local mirror of Project Gutenberg or if you want to process books that you have already downloaded. 
The script expect that the local data directory is organized as follows:
```
txt-files/
    ├── cache/
        └── epub/
            ├── {id_1}/
            │   └── pg{id_1}.txt.gz
            ├── {id_2}/
            │   └── pg{id_2}.txt.gz
            └── ...
```
Where `{id_1}`, `{id_2}`, etc. are the Gutenberg IDs of the books. The `pg{id}.txt.gz` files are the raw text files of the books.
The txt-files can be downloaded directly from the Project Gutenberg website : https://www.gutenberg.org/cache/epub/feeds/

#### Example
```bash
The downloaded books will be cleaned and saved as JSON files, ready for processing in the next step.
```bash
python download_books.py --mode local --output_dir ./books_to_process --limit 1 --local_data_dir <LOCAL_DATA_DIR>
```

### Search Configuration (`gutenberg_download/config/search_config.yaml`)

The search parameters for the books to download are specified in a YAML configuration file. This file allows you to filter books based on various criteria such as language, search terms, and topics.
You can also specify a list of ids to download specific books directly by their Gutenberg IDs.

The full list of parameters are those available in the [Gutendex API](https://gutendex.com).

**Example :**

```yaml
# Search for English books with 'adventure' in the topic or title
languages: en
search: adventure
```
### Step 2: Processing Books

Use the `text_processor/process_book.py` script to generate summaries and themes. This script takes the JSON files produced in Step 1 as input.
To see the available options, run the script with `--help`:

```bash
python process_books.py --help
```

#### Using Google Gemini (Recommended for Large Corpora or with limited local resources)

The Gemini API was used in the original project to process over 5,000 books due to its speed and ability to handle large contexts.

To use the Google Gemini API, you need to have an API key. To obtain one, follow the instructions on the [Google Gemini API documentation](https://developers.google.com/gemini/docs/get-started).

```bash
python process_books.py data/example_books \
  --model-type gemini \
  --api-key AIzaSyCMicWlikSjJnD2bwF0zT4hwnDShlWxunk \
  --model-name gemini-2.0-flash-lite \
  --chunk-size 28000 \
  --output ./example_processed_books 
```

#### Using a Local LLM with Ollama

This project also supports any model hosted locally via Ollama. 

Warning : Running large models locally requires significant computational resources, including a powerful GPU with sufficient VRAM. The recommended model for this project is Llama 3.1, which is available on Ollama.
Depending on your hardware, processing large books may take a long time. You may benefit from using smaller chunk sizes (e.g., 4096 or 2048) to reduce memory usage and processing time, but this may affect the quality of the summaries.
It's also recommended to use a model that can handle long contexts (at the very least 8K tokens), such as Llama 3.1.

To install and run Ollama, follow these steps:

1.  **Install Ollama**: Visit [Ollama's download page](https://ollama.com/download) and follow the instructions for your OS. For Linux, you can use:

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
2.  **Start the Ollama server**:

    ```bash
    ollama serve
    ```
3.  **Pull a model** (e.g., Llama 3.1):

    ```bash
    ollama pull llama3.1
    ```
    
Ensure the Ollama server is running before executing the script.

```bash

python process_books.py data/example_books --model-type ollama \
  --model-name llama3.1 \
  --chunk-size 8096 \
  --output ./processed_books_ollama 
```


### Prompts Configuration (`text_processor/config/prompts.yaml`)

This file contains the prompts used to instruct the LLM for summarization and theme extraction. You can edit this file to experiment with different instructions.

The file contains tree main prompts:

  * `chunk_summary`: Used for summarizing individual text chunks.
  * `intermediate_summary`: Used to combine summaries of chunks if combined summaries exceed the context window of the LLM.
  * `final_summary`: Used to combine the chunk summaries and extract themes.


## Input and Output Formats

The scripts use validated Pydantic schemas for data handling.
The pydantic models are defined in `text_processor/schemas.py` and ensure that the input and output JSON files conform to the expected structure.

### Input Format (`ProcessorInput`)

The input for the `text_processor` is a JSON file with the following structure:

```json
{
  "text": "The full, cleaned text of the book...",
  "title": "A Classic Novel",
  "authors": [
    {
      "name": "Jane Doe",
      "birth_year": 1800,
      "death_year": 1890
    }
  ],
  "gutenberg_id": 12345
}
```

### Output Format (`ProcessorOutput`)

The final output is a JSON file containing the generated analysis:

```json
{
  "summary": "This is the comprehensive, abstractive summary of the entire book generated by the LLM.",
  "title": "A Classic Novel",
  "authors": [
    {
      "name": "Jane Doe",
      "birth_year": 1800,
      "death_year": 1890
    }
  ],
  "themes": [
    "love",
    "betrayal",
    "social class",
    "redemption"
  ],
  "gutenberg_id": 12345
}
```
