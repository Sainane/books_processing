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
        procesor_output = ProcessorOutput(
            summary=output.summary,
            title=book.title,
            authors=book.authors,
            themes=output.themes,
            gutenberg_id=book.gutenberg_id,
        )
        print(f"Book '{book.title}' processed successfully")
        return  procesor_output

