"""
This module provides pydantic schemas used for processing to ensure data validity.

It includes a function to save book data to a JSON file, and defines the structure of book metadata returned by the Gutendex API.

Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, HttpUrl

class Person(BaseModel):
    """
    Represents an author or translator of a book.
    """
    birth_year: Optional[int] = Field(default= None, description="Year of birth, or null if unknown.")
    death_year: Optional[int] = Field(default= None, description="Year of death, or null if unknown.")
    name: str = Field(..., description="Full name of the person.")

class Book(BaseModel):
    """
    Represents a single book object from the Gutendex API.
    """
    id: int = Field(..., description="Project Gutenberg ID number.")
    title: str = Field(..., description="Title of the book.")
    subjects: List[str] = Field([], description="List of subjects for the book.")
    authors: List[Person] = Field([], description="List of authors, each a Person object.")
    summaries: List[str] = Field([], description="List of summaries for the book.") # Not explicitly in docs, but good to include if API can return it.
    translators: List[Person] = Field([], description="List of translators, each a Person object.")
    bookshelves: List[str] = Field([], description="List of bookshelves the book belongs to.")
    languages: List[str] = Field([], description="List of two-character language codes (e.g., 'en', 'fr').")
    copyright: Optional[bool] = Field(None, description="Copyright status: true (existing), false (public domain), or null (unknown).")
    media_type: str = Field(..., description="Type of media (e.g., 'Text').")
    formats: Dict[str, HttpUrl] = Field({}, description="Dictionary of MIME type to download URL for various formats.")
    download_count: int = Field(..., description="Number of downloads from Project Gutenberg.")

# 4. Define the main Gutendex Book List Response Model
class GutendexBookListResponse(BaseModel):
    """
    Represents the full response structure for a list of books from the Gutendex API.
    """
    count: int = Field(..., description="Total number of books for the query on all pages combined.")
    next: Optional[HttpUrl] = Field(None, description="URL to the next page of results, or null if no next page.")
    previous: Optional[HttpUrl] = Field(None, description="URL to the previous page of results, or null if no previous page.")
    results: List[Book] = Field([], description="Array of Book objects for the current page.")

def save_books_to_json(books: List[Book], filename: str):
    """
    Saves a list of Book objects to a JSON file.

    Args:
        books (List[Book]): A list of Book Pydantic models.
        filename (str): The path to the output JSON file.
    """

    books_data = [book.model_dump(mode="json") for book in books]

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(books_data, f, ensure_ascii=False, indent=4)
    print(f"Successfully saved {len(books)} books to '{filename}'.")