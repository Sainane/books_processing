# Text Analysis and Processing Suite

This repository contains a comprehensive suite of tools designed for the ingestion, processing, and analysis of books textual data. It's built with modularity in mind, allowing for flexible integration of different components.


## Overview

This project is divided into two primary, interconnected modules:

1.  **Gutenberg Download Sub-Project**: Handles the acquisition and initial cleaning of book data from Project Gutenberg, preparing it for downstream processing.
2.  **Text Processor**: A modular Python tool for advanced text analysis, including hierarchical summarization and theme extraction, leveraging large language models (LLMs).


## 📚 Gutenberg Download Sub-Project

This module is responsible for obtaining book texts and their metadata from Project Gutenberg. It offers flexible modes for data acquisition and ensures the text is clean and standardized for further analysis.

For detailed information on features, installation, and usage, please refer to the dedicated [README.md](gutenberg_download/README.md)


## 📝 Text Processor

The core of this suite, the `Text Processor`, provides robust capabilities for understanding and distilling large volumes of text. It integrates with various LLMs (like Gemini or Ollama) to perform advanced summarization and theme extraction.

For comprehensive details on features, requirements, installation, and usage, please refer to the dedicated : [README.md](text_processor/README.md) 

## Getting Started

To utilize this suite, you'll generally follow these steps:

1.  **Acquire Data**: Use the **Gutenberg Download Sub-Project** to fetch and clean book texts, saving them in the specified structured JSON format.
2.  **Process Text**: Utilize the **Text Processor** to perform hierarchical summarization and theme extraction on the prepared JSON files.

We recommend reviewing the individual READMEs for each sub-project for specific installation and usage instructions.

But first you can start by installing the required dependencies:

```bash
pip install -r requirements.txt
```

### Quick example with gemini

You can quickly test the functionality of the text processor with a sample book:

First, download a sample book from Project Gutenberg using the `gutenberg_download` module. You can use the following command to download a book. The book will be downloaded
to the directory `./quick_start_book`.

```bash
python gutenberg_download/main.py --mode online --output_dir ./quick_start_book --limit 1 --search_config ./gutenberg_download/config/quick_start_config.yaml
```

And add you gemini api key and run the command to process the downloaded book (add your gemini api key). The
book will be processed and the output will be saved in the directory `./quick_start_processed_data`.

```bash
python text_processor/process_book.py ./quick_start_book --model-type gemini --chunk-size 28000 --api-key <GEMINI_API_KEY> --model-name gemini-2.0-flash --output ./quick_start_processed_data --prompts-config ./text_processor/config/prompts.yaml
```
