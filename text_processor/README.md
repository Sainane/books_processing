# Text Processor

A modular Python tool for hierarchical summarization and theme extraction from books using LLMs (Gemini, Ollama).

-----

## Features

  - Hierarchical summarization of large texts
  - Theme extraction
  - Support for multiple LLMs (Gemini, Ollama)
  - Chunking for efficient processing
  - Structured output with Pydantic models

-----

## Requirements

  - Python 3.10+
  - pip
  - [NLTK](https://www.nltk.org/) (for tokenization)
  - LLM API keys (e.g., for Gemini)

-----

## Installation

```bash
pip install -r ../requirements.txt
python -m nltk.downloader punkt
```

-----

## Ollama Installation and Usage

To use Ollama as an LLM backend, you'll need to install and run the Ollama server locally.

### 1\. Install Ollama

Visit [https://ollama.com/download](https://ollama.com/download) and follow the instructions for your OS. For Linux, you can use:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2\. Start the Ollama Server

Run the server in your terminal:

```bash
ollama serve
```

### 3\. Pull a Model

Download a model (e.g., Llama 3.1):

```bash
ollama pull llama3.1
```

### Using Ollama with This Project

Once Ollama is running and you've pulled a model, use the following command structure:

```bash
python process_book.py <input_folder_or_file> \
  --model-type ollama \
  --model-name llama3.1 \
  --chunk-size 1000 \
  --summary-length 800 \
  --prompts-config /config/prompts.yaml \
  --output <output_folder> \
  --structured-output \
  --verbose
```

  - If your Ollama server isn't on the default URL, use `--ollama-url` to specify it.
  - **Note:** Ollama must be running before you execute the processing command.

-----

## Gemini Usage

### How to Obtain Your Gemini API Key

To use Gemini models, you'll need a Gemini API key, which you can get for free from Google AI Studio.

1.  **Visit Google AI Studio**: Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2.  **Sign in**: Use your Google account.
3.  **Create API Key**: Look for a button like "Create API Key in new project."
4.  **Copy and Secure Your Key**: Copy the generated API key immediately and store it securely. **Do not expose your API key publicly or commit it directly into your code.**

### Using Gemini with This Project

Once you have your API key, you can use it with the `--api-key` argument, or set it as an environment variable (e.g., `GEMINI_API_KEY`) for the `text_processor` to pick up automatically.

```bash
python process_book.py <input_folder_or_file> \
  --model-type gemini \
  --api-key <YOUR_GEMINI_API_KEY> \
  --model-name gemini-2.5-flash-lite-preview-06-17 \
  --chunk-size 28000 \
  --summary-length 800 \
  --prompts-config text_processor/config/prompts.yaml \
  --output <output_folder> \
  --structured-output \
  --verbose
```

-----

## Command Line Arguments

  - `input_folder_or_file`: Path to a `.json` or `.gz` file, or a folder containing such files. (Required)
  - `--model-type`: Specifies the LLM to use (`gemini` or `ollama`). (Default: `gemini`)
  - `--api-key`: Your Gemini API key. **Required for Gemini models.**
  - `--model-name`: The specific model name to use (e.g., `gemini-2.5-flash-lite-preview-06-17` for Gemini, `llama3.1` for Ollama).
  - `--ollama-url`: The URL of your Ollama server. (Default: `http://localhost:11434` for Ollama models)
  - `--chunk-size`: The maximum number of tokens per text chunk. (Default: `28000`)
  - `--summary-length`: The target length for summaries in words. (Default: `800`)
  - `--prompts-config`: Path to the YAML configuration file for AI prompts. (Default: `text_processor/config/prompts.yaml`)
  - `--output`, `-o`: The output folder. If not specified, results are printed to stdout.
  - `--structured-output`: Use structured output for the model. (Default: `True`)
  - `--verbose`, `-v`: Enable verbose output for detailed logs.

-----

## Project Structure

  - `text_processor/core/`
      - `book_processor.py`: Orchestrates summarization and extraction.
      - `chunker.py`: Handles sentence-based text chunking.
      - `language_model.py`: Interfaces for various LLM backends.
      - `schemas.py`: Defines Pydantic data models for input/output.
      - `summarizer.py`: Contains the hierarchical summarization logic.
  - `text_processor/process_book.py`: The main command-line interface entry point.
  - `text_processor/config/prompts.yaml`: Default configuration file for AI prompts.

-----

## Prompts Configuration

Prompts for summarization and theme extraction are loaded from a YAML configuration file. The default path is `text_processor/config/prompts.yaml`. You can customize these prompts by editing this file or by providing your own via the `--prompts-config` argument.

For example, to use a custom prompts file:

```bash
python process_book.py <input_folder_or_file> --prompts-config /path/to/your/custom_prompts.yaml ...
```

-----

## Input and Output Formats

Here are detailed examples of the input and output JSON formats based on the `ProcessorInput` and `ProcessorOutput` schemas.

### Input Format (`ProcessorInput`)

Each input file should be a JSON object with the following structure:

```json
{
  "text": "Full text of the book goes here.",
  "title": "Book Title",
  "authors": [
    {
      "name": "Author Name",
      "birth_year": 1850,
      "death_year": 1920
    }
  ],
  "gutenberg_id": 12345
}
```

  - `text`: The complete text to process (string).
  - `title`: Title of the book (string).
  - `authors`: List of author objects, each with at least a `name`. Other fields (like `birth_year`, `death_year`) depend on your `Person` schema.
  - `gutenberg_id`: (Optional) The Project Gutenberg ID (integer).

### Output Format (`ProcessorOutput`)

The output will be a JSON object like:

```json
{
  "summary": "A concise summary of the book.",
  "title": "Book Title",
  "authors": [
    {
      "name": "Author Name",
      "birth_year": 1850,
      "death_year": 1920
    }
  ],
  "themes": [
    "Theme 1",
    "Theme 2"
  ],
  "gutenberg_id": 12345
}
```

  - `summary`: The generated summary (string).
  - `title`: Title of the book (string).
  - `authors`: List of author objects (same as input).
  - `themes`: List of identified themes (array of strings).
  - `gutenberg_id`: (Optional) The Project Gutenberg ID (integer).

Refer to `text_processor/core/schemas.py` for the full schema details.