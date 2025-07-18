# Text Processor

A modular Python tool for hierarchical summarization and theme extraction from books using LLMs (Gemini, Ollama, TogetherAI).

## Features

- Hierarchical summarization of large texts
- Theme extraction
- Support for multiple LLM (Gemini, Ollama)
- Chunking for efficient processing
- Structured output with Pydantic models

## Requirements

- Python 3.10+
- pip
- [NLTK](https://www.nltk.org/) (for tokenization)
- LLM API keys (ex for Gemini)

## Installation

```bash
pip install -r requirements.txt
python -m nltk.downloader punkt
```
To use Ollama as an LLM backend, you need to install and run the Ollama server locally. Here are the steps:

## Ollama Installation

1. **Install Ollama**  
   Visit [https://ollama.com/download](https://ollama.com/download) and follow the instructions for your OS.  
   For Linux, you can use:

   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Start the Ollama Server**  
   Run the server in your terminal:

   ```bash
   ollama serve
   ```

3. **Pull a Model**  
   Download a model (e.g., Llama 3.1):

   ```bash
   ollama pull llama3.1
   ```

## Using Ollama with This Project

- In your command, set `--model-type ollama` and specify the model name (e.g., `llama3`):

   ```bash
   python process_book.py <input_folder_or_file> \
     --model-type ollama \
     --model-name llama3 \
     --chunk-size 1000 \
     --summary-length 800 \
     --output <output_folder> \
     --structured-output \
     --verbose
   ```

- If your Ollama server is not on the default URL, use `--ollama-url` to specify it.

**Note:** Ollama must be running before you execute the processing command.
## Using Gemini with this project

```bash
python process_book.py <input_folder_or_file>  --model-type gemini --api-key <YOUR_GEMINI_API_KEY> --model-name gemini-2.5-flash-lite-preview-06-17 --chunk-size 28000 --summary-length 800 --output <output_folder> --structured-output  --verbose
```

- `input_folder_or_file`: Path to a `.json` or `.gz` file, or a folder containing such files.
- `--model-type`: `gemini` or `ollama`
- `--api-key`: Required for Gemini models
- `--model-name`: Model name (see CLI help for options)
- `--output`: Output folder (optional; prints to stdout if omitted)
- `--chunk-size`: Max tokens per chunk
- `--summary-length`: Target summary length (words)
- `--structured-output`: Use structured output (default: True)
- `--verbose`: Print detailed logs

## Project Structure

- `text_processor/core/`
  - `book_processor.py`: Orchestrates summarization and extraction
  - `chunker.py`: Sentence-based text chunking
  - `language_model.py`: LLM backend interfaces
  - `schemas.py`: Pydantic data models
  - `summarizer.py`: Hierarchical summarization logic
- `text_processor/process_book.py`: CLI entry point

## Prompts

Prompts for summarization are loaded from `prompts/prompts.yaml`. Customize as needed.

Here are detailed examples of the input and output JSON formats for your project, based on the `ProcessorInput` and `ProcessorOutput` schemas.

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