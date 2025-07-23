import gzip
import json
import argparse
import os.path
from pathlib import Path

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
                f.write(result.model_dump_json(indent=2))
            else:
                json.dump(result, f, indent=2, ensure_ascii=True)

        print(f"Result saved to: {output_path}")
    else:
        if hasattr(result, 'model_dump_json'):
            print(result.model_dump_json(indent=2))
        else:
            print(json.dumps(result, indent=2, ensure_ascii=True))


def create_model(model_type, model_name, api_key, base_url):
    """Create the appropriate model based on type."""
    if model_type.lower() == 'gemini':
        if not api_key:
            raise ValueError("API key is required for Gemini models")
        return GeminiModel(
            api_key=api_key,
            model_name=model_name,
        )
    elif model_type.lower() == 'ollama':
        return OllamaModel(
            model_name=model_name,
            ollama_base_url=base_url,
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
        "--output",
        "-o",
        help="Output folder (if not specified, prints to stdout)."
    )



    args = parser.parse_args()

    if not args.model_name:
        if args.model_type == 'gemini':
            args.model_name = "gemini-2.5-flash-lite-preview-06-17"
        else: # Default for Ollama
            args.model_name = "llama3.1"

    # Validate API key for Gemini
    if args.model_type == 'gemini' and not args.api_key:
        parser.error("--api-key is required when using Gemini models")

    try:
        print(f"Using {args.model_type} model: {args.model_name}")
        try:
            # Create the AI model instance
            model = create_model(
                model_type=args.model_type,
                model_name=args.model_name,
                api_key=args.api_key,
                base_url=args.ollama_url,
            )

            chunker = ChunkerImpl(chunk_size=args.chunk_size)
            summarizer = HierarchicalSummarizer(
                model=model,
                chunker=chunker
            )
            processor = BookProcessor(summarizer=summarizer)
        except ValueError as e:
            print(f"Error creating model: {e}")
            return
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
            print("No JSON")
            return

        for file in files_to_process:
            output_dir_path = Path(args.output) if args.output else None
            if output_dir_path:
                output_dir_path.mkdir(parents=True, exist_ok=True)

            print(f"Processing file {file.name}...")
            try:
                book_data = load_book_data(file)
                book = ProcessorInput.model_validate(book_data)

                result = processor.process(book)
                output_file_name = f"{model.get_name()}_processed_{file.name}"
                file_path = os.path.join(output_dir_path, output_file_name) if output_dir_path else os.path.join("book_processor_output", output_file_name)
                save_result(result, file_path)
            except Exception as e:
                print(f"Error processing file {file.name}: {e}")


    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()