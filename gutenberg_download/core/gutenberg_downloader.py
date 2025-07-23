"""
This module provides the GutenbergDownloader class for downloading books from Project Gutenberg,

It supports both online and local file retrieval modes, cleaning the text, and saving it in a structured format.



Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from urllib.parse import urlencode
import httpx
import gzip
import json
import re
import os

import requests

from common.load_config import load_yaml_config
from gutenberg_download.core.metadata_schema import Book, GutendexBookListResponse
from text_processor.core.schemas import ProcessorInput


class GutenbergDownloader(ABC):
    def __init__(self, metadata_url="https://gutendex.com/"):
        self.metadata_url = metadata_url
        self.search_params = load_yaml_config("gutenberg_download/config/search_config.yaml")

    @staticmethod
    def get_books_metadata(limit: int, search_params) -> list[Book]:
        """
        Retrieves metadata for a book by its Gutenberg ID.
        :param search_params:
        :param limit:
        :return: A Book object containing metadata, or None if not found.
        """
        books_retrieved = list[Book]()
        custom_timeout_dict = httpx.Timeout(
            connect=50.0,
            read=50.0,
            write=15.0,
            pool=5.0
        )

        url = "https://gutendex.com/books/?" + urlencode(search_params)
        while len(books_retrieved) < limit and url:
            response = httpx.get(url, timeout=custom_timeout_dict)
            data = response.json()
            response_value = GutendexBookListResponse.model_validate(data)
            books = [Book.model_validate(book) for book in response_value.results]
            current_number_of_books = len(books_retrieved)
            books_retrieved.extend(books[0:max(0, limit - current_number_of_books)])
            url = data.get("next")
        return books_retrieved


    @staticmethod
    def clean_gutenberg_text(text: str) -> str:
        """
        Cleans raw text from Project Gutenberg files by:
        1. Removing common Project Gutenberg header and footer boilerplate.
        2. Replacing single newlines (line wraps) with spaces to form continuous paragraphs.
        3. Normalizing multiple newlines to represent distinct paragraph breaks (double newlines).

        Args:
            text (str): The raw text read from a Project Gutenberg file.

        Returns:
            str: The cleaned text, ready for sentence tokenization and chunking.
        """
        # Remove header
        start_match = re.search(r'\*\*\* ?START OF TH(E|IS) PROJECT GUTENBERG EBOOK.*?\*\*\*', text,
                                re.IGNORECASE | re.DOTALL)
        if start_match:
            text = text[start_match.end():]

        # Remove footer
        end_match = re.search(r'\*\*\* ?END OF TH(E|IS) PROJECT GUTENBERG EBOOK.*', text, re.IGNORECASE | re.DOTALL)
        if end_match:
            text = text[:end_match.start()]

        # Remove various boilerplate lines that might remain
        text = re.sub(r'Project Gutenberg-tm Etexts are often prepared from several editions\..*', '', text,
                      flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'The Project Gutenberg EBook of .*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'End of the Project Gutenberg EBook of .*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'\[This Etext was prepared by .*\].*', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Produced by \w+ from images generously made available by \w+\.', '', text,
                      flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'Transcribed from the original by \w+\.', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'(\n\s*)*\*\*\* END OF THE PROJECT GUTENBERG EBOOK .*', '', text,
                      flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'(\n\s*)*\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*', '', text,
                      flags=re.DOTALL | re.IGNORECASE)


        text = text.replace('\r\n', '\n')
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        text = re.sub(r'\n\s*\n+', 'PARAGRAPH_BREAK_PLACEHOLDER', text)
        text = re.sub(r'\n', ' ', text)
        text = text.replace('PARAGRAPH_BREAK_PLACEHOLDER', ' ')

        # Clean up extra spaces
        text = re.sub(r' {2,}', ' ', text)
        text = text.strip()

        return text

    @abstractmethod
    def get_book_text(self, book: Book) -> str:
        pass

    def download_books(self, output_dir: str, limit: int) -> None:
        """
        Downloads a book from Project Gutenberg, cleans the text, and saves it as a JSON file.
        :param limit:
        :param output_dir: The directory where the cleaned book JSON file will be saved.
        """

        books = self.get_books_metadata(limit=limit, search_params=self.search_params)

        for book in books:
            try:
                book_id = book.id
                text = self.get_book_text(book)

            except Exception as e:
                print(f"Error processing book {book.id}: {e}")
                continue

            if not text:
                print(f"No text found for book {book_id}. Skipping.")
                continue


            cleaned_text = self.clean_gutenberg_text(text)
            process_input = ProcessorInput(text=cleaned_text,title=book.title, authors=book.authors, gutenberg_id=book_id)
            output_file_path = os.path.join(output_dir, f"{book_id}.json")
            os.makedirs(output_dir, exist_ok=True)
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(process_input.model_dump(mode="json"), f, ensure_ascii=False, indent=2)  # indent for readability
            print(f"Successfully saved online book {book_id} to '{output_file_path}'.")

class GutenbergDownloaderOnline(GutenbergDownloader):
    """
    A class to download books from Project Gutenberg (online or local .txt.gz)
    and clean the text for further processing.
    """
    def __init__(self, metadata_url="https://gutendex.com/"):
        super().__init__(metadata_url)
    def get_book_text(self, book: Book) -> str:
        """
        Retrieves the text content of a book from its metadata.
        :param book: The Book object containing metadata.
        :return: The raw text content of the book.
        """
        text_url = book.formats.get("text/plain; charset=utf-8")
        if not text_url:
            text_url = book.formats.get("text/plain; charset=us-ascii")

        if not text_url:
            raise ValueError(f"Book {book.id} does not have a suitable plain text format available.")

        try:
            response = requests.get(str(text_url), timeout=60)
            response.raise_for_status()
            try:
                text = response.content.decode("utf-8")
            except UnicodeDecodeError:
                text = response.content.decode("latin-1")
            return text
        except requests.RequestException as e:
            raise ValueError(f"Failed to retrieve book {book.id} content from {text_url}: {e}")

class GutenbergDownloaderLocal(GutenbergDownloader):
    def __init__(self, local_files_directory: str, metadata_url="https://gutendex.com/"):
        super().__init__(metadata_url)
        self.local_files_directory = local_files_directory

    @staticmethod
    def _get_book_content_from_local_gzip(file_path: str) -> str:
        """
        Reads and decompresses content from a local .txt.gz file.
        This is a helper for local file processing.
        :param file_path: The path to the local .txt.gz file.
        :return: The raw text content of the book.
        """
        try:
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                text = f.read()
            print(f"Successfully read content from local file: '{file_path}'")
            return text
        except FileNotFoundError:
            raise FileNotFoundError(f"Local file not found: '{file_path}'")
        except Exception as e:
            raise IOError(f"Error reading or decompressing local file '{file_path}': {e}")
    def get_book_text(self, book: Book) -> str:
        """
        Retrieves the text content of a book from its metadata.
        :param book: The Book object containing metadata.
        :return: The raw text content of the book.
        """
        file_name = f"pg{book.id}.txt.gz"
        file_path = os.path.join(self.local_files_directory, str(book.id), file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file for book {book.id} not found at {file_path}")

        return self._get_book_content_from_local_gzip(file_path)
