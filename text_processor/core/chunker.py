"""
This module provides a class for chunking text into smaller pieces based on a specified maximum number of tokens.

The Chunker class is an abstract base class that defines the interface for chunking text.
It includes a concrete implementation, ChunkerImpl, which uses NLTK to tokenize text into sentences and words,

Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from nltk.tokenize import sent_tokenize, word_tokenize

class Chunker(ABC):
    """Abstract base class for chunking text."""
    def __init__(self, chunk_size: int):
        """
        Initializes the Chunker with a specified chunk size.
        :param chunk_size: The maximum number of tokens per chunk. Must be a positive integer.
        """
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        self.chunk_size = chunk_size
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
       pass

    def get_chunk_size(self) -> int:
        """
        Returns the maximum number of tokens per chunk.
        :return: The chunk size as an integer.
        """
        return self.chunk_size
class ChunkerImpl(Chunker):
    """Concrete implementation of the Chunker class that splits text into chunks based on sentences."""
    def __init__(self, chunk_size: int = 1000):
        """
        Initializes the Chunker with a specified chunk size.
        :param chunk_size: The maximum number of tokens per chunk. Must be a positive integer.
        """
        super().__init__(chunk_size)


    def chunk(self, text: str) -> list[str]:
        """
        Splits the input text into sentences and then chunks these sentences
        :param text: The input text to be chunked.
        :return: A list of text chunks, where each chunk is a string.
        """
        if not isinstance(text, str):
            raise TypeError("Input 'text' must be a string.")


        sentences = sent_tokenize(text)

        chunks = []
        current_chunk_sentences = []
        current_chunk_token_count = 0

        for sentence in sentences:

            sentence_tokens = word_tokenize(sentence)
            sentence_token_count = len(sentence_tokens)

            if (current_chunk_token_count + sentence_token_count <= self.chunk_size) or not current_chunk_sentences:

                current_chunk_sentences.append(sentence)
                current_chunk_token_count += sentence_token_count
            else:

                chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = [sentence]
                current_chunk_token_count = sentence_token_count

        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

        return chunks
