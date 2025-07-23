"""
This script serves as the main entry point for downloading and processing books from Project Gutenberg.

Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

import argparse
import os
import sys

from gutenberg_download.core.gutenberg_downloader import GutenbergDownloaderOnline, GutenbergDownloaderLocal

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    parser = argparse.ArgumentParser(
        description="Download and process books from Project Gutenberg (online or local)."
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["online", "local"],
        required=True,
        help="Choose download mode: 'online' for API-based download, 'local' for processing local .txt.gz files.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="processed_books",
        help="Directory to save the processed JSON book files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of books to process/download. (Applies to both modes).",
    )
    parser.add_argument(
        "--metadata_url",
        type=str,
        default="https://gutendex.com/",
        help="Base URL for the Gutendex API. (Applies to both online and local modes for metadata retrieval).",
    )


    # Arguments specific to 'local' mode
    parser.add_argument(
        "--local_data_dir",
        type=str,
        help="Path to the directory containing local Project Gutenberg .txt.gz files. Required for 'local' mode.",
    )

    args = parser.parse_args()

    downloader = None

    if args.mode == "online":
        print(f"Running in ONLINE mode. Fetching up to {args.limit} books.")
        print(f"Using Gutendex metadata URL: {args.metadata_url}")
        downloader = GutenbergDownloaderOnline(metadata_url=args.metadata_url)
        downloader.download_books(
            output_dir=args.output_dir,
            limit=args.limit,
        )
    elif args.mode == "local":
        if not args.local_data_dir:
            parser.error("--local_data_dir is required for 'local' mode.")
        if not os.path.isdir(args.local_data_dir):
            parser.error(f"Local data directory '{args.local_data_dir}' does not exist or is not a directory.")

        print(f"Running in LOCAL mode. Processing up to {args.limit} books from '{args.local_data_dir}'.")
        print(f"Using Gutendex metadata URL: {args.metadata_url}")

        downloader = GutenbergDownloaderLocal(
            local_files_directory=args.local_data_dir, metadata_url=args.metadata_url
        )
        downloader.download_books(
            output_dir=args.output_dir,
            limit=args.limit,
        )
    else:
        print("Invalid mode selected. Please choose 'online' or 'local'.")
        sys.exit(1)

    print("\nDownloader script finished.")


if __name__ == "__main__":
    main()