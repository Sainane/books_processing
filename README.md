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

### Example