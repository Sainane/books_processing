from typing import List, Optional

from pydantic import BaseModel, Field

from gutenberg_download.core.metadata_schema import Person


class ProcessorInput(BaseModel):
    """
    Represents the input for a text processing operation.
    """
    text: str = Field(..., description="The text to be processed.")
    title: str = Field(default_factory=str, description="The title of the text.")
    authors: List[Person] = Field(default_factory=list, description="List of authors of the text.")
    gutenberg_id: Optional[int] = Field(..., description="The Gutenberg ID of the text.")
    class Config:
        from_attributes = True

class ProcessorOutput(BaseModel):
    """
    Represents the output of a text processing operation.
    """
    summary: str = Field(default_factory=str, description="The summarization output.")
    title: str = Field(default_factory=str, description="The title of the text.")
    authors: List[Person] = Field(default_factory=list, description="List of authors of the text.")
    themes: list[str] = Field(default_factory=list, description="List of themes identified in the text")
    gutenberg_id: Optional[int] = Field(..., description="The Gutenberg ID of the text.")

class SummarizerOutput(BaseModel):
    """
    Represents the output of a summarization operation.
    """
    summary: str = Field(default_factory=str, frozen=True,description="The summarization output.")
    themes: list[str] = Field(default_factory=list, frozen=True, description="List of themes identified in the text")


    def __repr__(self):
        return f"SummarizerOutput(summary={self.summary})"



class SummarizerInput(BaseModel):
    """
    Represents the input for a summarization operation.
    """
    title: str = Field(..., description="The title of the text to be summarized.")
    authors: List[Person] = Field(..., description="The author of the text to be summarized.")
    text: str = Field(..., description="The text to be summarized.")
    gutenberg_id: int = Field(description="The Gutenberg ID.")
