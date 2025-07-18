import gzip
import json
import argparse
import os.path
from pathlib import Path

# Assume these imports are correct based on your project structure
from text_processor.core.book_processor import BookProcessor
from text_processor.core.chunker import ChunkerImpl
from text_processor.core.language_model import GeminiModel, OllamaModel
from text_processor.core.schemas import ProcessorInput
from text_processor.core.summarizer import HierarchicalSummarizer


def load_book_data(folder_path):
    """Load book data from JSON or compressed JSON file."""
    file_path = Path(folder_path)

    if file_path.suffix == '.gz':
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def save_result(result, output_path):
    """Save processing result to file."""
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            if hasattr(result, 'model_dump_json'):
                # Pydantic v2 method
                f.write(result.model_dump_json(indent=2))
            else:
                json.dump(result, f, indent=2, ensure_ascii=True)

        print(f"Result saved to: {output_path}")
    else:
        if hasattr(result, 'model_dump_json'):
            print(result.model_dump_json(indent=2))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=True))


def create_model(model_type, model_name, api_key, base_url, structured_output):
    """Create the appropriate model based on type."""
    if model_type.lower() == 'gemini':
        if not api_key:
            raise ValueError("API key is required for Gemini models")
        return GeminiModel(
            api_key=api_key,
            model_name=model_name,
            structured_output=structured_output
        )
    elif model_type.lower() == 'ollama':
        return OllamaModel(
            model_name=model_name,
            ollama_base_url=base_url,
            structured_output=structured_output
        )
    else:
        raise ValueError(f"Unsupported model type: {model_type}")


def main():
    parser = argparse.ArgumentParser(
        description="Process books using hierarchical summarization with Gemini or Ollama models",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "input_folder",
        help="Directory or file path containing book data in JSON format."
    )

    # Model selection
    parser.add_argument(
        "--model-type",
        choices=['gemini', 'ollama'],
        default='gemini',
        help="Type of model to use (gemini or ollama)"
    )

    # Gemini-specific arguments
    parser.add_argument(
        "--api-key",
        help="Gemini API key (required for Gemini models)"
    )

    parser.add_argument(
        "--model-name",
        help="Model name to use. For Gemini: gemini-2.5-flash-lite-preview-06-17, gemini-pro, etc. For Ollama: llama3.1, mistral, etc."
    )

    # Ollama-specific arguments
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama server URL (for Ollama models)"
    )

    # Processing arguments
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=28000,
        help="Chunk size for text processing"
    )

    parser.add_argument(
        "--summary-length",
        type=int,
        default=800,
        help="Target length for summaries"
    )

    # NEW: Argument for prompts config file
    parser.add_argument(
        "--prompts-config",
        type=str,
        default="text_processor/config/prompts.yaml", # Default path within your project structure
        help="Path to the YAML configuration file for AI prompts."
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output folder (if not specified, prints to stdout)."
    )

    parser.add_argument(
        "--structured-output",
        action="store_true", # Use store_true for boolean flags that are True if present
        default=True,        # Set default to True as per your existing code
        help="Use structured output for the model"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Set default model name if not provided
    if not args.model_name:
        if args.model_type == 'gemini':
            args.model_name = "gemini-2.5-flash-lite-preview-06-17"
        else: # Default for Ollama
            args.model_name = "llama3.1"

    # Validate API key for Gemini
    if args.model_type == 'gemini' and not args.api_key:
        parser.error("--api-key is required when using Gemini models")

    try:
        if args.verbose:
            print(f"Using {args.model_type} model: {args.model_name}")
            print(f"Prompts configuration file: {args.prompts_config}")

        # Create the AI model instance
        model = create_model(
            model_type=args.model_type,
            model_name=args.model_name,
            api_key=args.api_key,
            base_url=args.ollama_url,
            structured_output=args.structured_output
        )

        chunker = ChunkerImpl(chunk_size=args.chunk_size)
        summarizer = HierarchicalSummarizer(
            model=model,
            chunker=chunker,
            prompts_config_file=args.prompts_config,
            summary_length=args.summary_length
        )
        processor = BookProcessor(summarizer=summarizer)

        input_path = Path(args.input_folder)
        if input_path.is_file():
            files_to_process = [input_path]
        elif input_path.is_dir():
            files_to_process = [f for f in input_path.iterdir()
                                if f.is_file() and f.suffix in ['.json']] # Added .json.gz
        else:
            print(f"Error: Input folder/file '{args.input_folder}' does not exist or is not a valid path.")
            return


        if not files_to_process:
            print("No JSON or JSON.GZ files found to process in the specified input.")
            return

        for file in files_to_process:
            output_dir_path = Path(args.output) if args.output else None
            if output_dir_path:
                output_dir_path.mkdir(parents=True, exist_ok=True)
                output_file_path = output_dir_path / file.name
            else:
                output_file_path = None

            if output_file_path and output_file_path.is_file():
                print(f"File {file.name} already exists in output directory. Skipping.")
                continue

            print(f"Processing file {file.name}...")
            try:
                book_data = load_book_data(file)
                book = ProcessorInput.model_validate(book_data)

                result = processor.process(book)
                save_result(result, output_file_path)
            except Exception as e:
                print(f"Error processing file {file.name}: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()