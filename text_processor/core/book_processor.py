"""
This module provides the BookProcessor class for processing books formatted as ProcessorInput.

It takes a book's text, title, authors, and optional Gutenberg ID, and uses a Summarizer to generate a summary and identify themes and
returns a ProcessorOutput object containing the summary, title, authors, themes, and optional Gutenberg ID.



Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""


from text_processor.core.schemas import ProcessorInput, ProcessorOutput, SummarizerOutput
from text_processor.core.summarizer import Summarizer


class BookProcessor:
    def __init__(self, summarizer: Summarizer):
        self.summarizer = summarizer

    def process(self, book: ProcessorInput) -> ProcessorOutput:
        """
        Processes a book by summarizing its text and extracting relevant information.
        :param book: ProcessorInput object containing book details.
        :return: ProcessorOutput object containing the summary, title, authors, and themes.
        """
        result = self.summarizer.summarize(book.text)
        output = SummarizerOutput.model_validate(result)
        processor_output = ProcessorOutput(
            summary=output.summary,
            title=book.title,
            authors=book.authors,
            themes=output.themes,
            gutenberg_id=book.gutenberg_id,
        )
        print(f"Book '{book.title}' processed successfully")
        return  processor_output

