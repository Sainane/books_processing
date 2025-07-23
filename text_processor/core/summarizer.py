"""
The Summarizer module provides an abstract base class for summarization tasks and a concrete implementation for hierarchical summarization.

Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

import json
import re
from abc import ABC, abstractmethod
from typing import List
from tqdm import tqdm

from common.load_config import load_yaml_config
from text_processor.core.chunker import Chunker
from text_processor.core.language_model import LanguageModel
from text_processor.core.schemas import SummarizerOutput
from count_tokens.count import count_tokens_in_string


class Summarizer(ABC):
    def __init__(self, model: LanguageModel, chunker: Chunker):
        """
        Initializes the Summarizer with a language model, chunker, and summary length.
        :param model: The language model to be used for summarization.
        :param chunker: The chunker to split the text into manageable pieces.
        """
        self.model = model
        self.chunker = chunker
        self.token_limit = model.get_max_tokens() - 100  # Margin for safety

        if self.token_limit < chunker.get_chunk_size():
            raise ValueError(f"Chunk size {chunker.get_chunk_size()} exceeds model's token limit {self.token_limit}. "
                             f"Please adjust the chunk size or use a model with a higher token limit.")

    @abstractmethod
    def summarize(self, text: str) -> SummarizerOutput:
        pass
    @staticmethod
    def parse_json_output(json_output):
        """
        Parses the JSON output from the model and returns a structured dictionary.
        Handles both raw JSON and JSON wrapped in code blocks.
        """
        pattern = r'```(?:\w+)?\s*\n?(.*?)\n?```'
        match = re.search(pattern, json_output, re.DOTALL)
        try:
            if match:
                res = json.loads(match.group(1).strip())
            else:
                res = json.loads(json_output)
            return SummarizerOutput.model_validate(res)
        except json.JSONDecodeError:
            raise ValueError(f"Model output could not be parsed as JSON: {json_output}")


class HierarchicalSummarizer(Summarizer):
    """
    HierarchicalSummarizer is a concrete implementation of the Summarizer class that performs hierarchical summarization.
    It divides the input text into smaller chunks, generates intermediate summaries for each chunk, and then combines these summaries into a final summary, and list of themes.
    """
    def __init__(self, model: LanguageModel, chunker: Chunker):
        """
        Initializes the HierarchicalSummarizer with a language model, chunker, prompts configuration file, and summary length.
        :param model: The language model to be used for summarization.
        :param chunker: The chunker to split the text into manageable pieces.
        """
        super().__init__(model, chunker)
        self.prompts = load_yaml_config("text_processor/config/prompts.yaml")

    def summarize(self, text) -> SummarizerOutput:
        """
        Summarizes the input text by first chunking it into smaller pieces, then generating intermediate summaries for each chunk,
        The intermediate summaries are then combined and summarized into a final summary.
        If the combined intermediate summaries exceed the maximum token limit for the model, it recursively summarizes the chunks until it fits.
        :param text: The input text to be summarized.
        :return: The final summary and themes extracted from the text.
        """
        print("\nStarting hierarchical summarization...")
        intermediate_summaries = self.summarize_chunks(text, "chunk_summary")
        combined_intermediate_summaries = "\n\n".join(intermediate_summaries)
        max_length = self.token_limit - count_tokens_in_string(
            "final_summary") - count_tokens_in_string(json.dumps(SummarizerOutput.model_json_schema()))

        while count_tokens_in_string(combined_intermediate_summaries) > max_length:
            number_of_chunks = len(intermediate_summaries)
            print("\nCombined intermediate summaries exceed token limit, summarizing again...")
            intermediate_summaries = self.summarize_chunks(combined_intermediate_summaries, "intermediate_summary")
            new_number_of_chunks = len(intermediate_summaries)
            if new_number_of_chunks == number_of_chunks:
                raise ValueError("Unable to reduce the number of chunks further. Aborting... This may indicate that the text is too complex or lengthy for the current summarization strategy.")
            combined_intermediate_summaries = "\n\n".join(intermediate_summaries)

        print("\nGenerating final summary and themes...")
        final_prompt = self.prompts.get("final_summary").format(
            summaries=combined_intermediate_summaries,
        )
        json_output = self.model.generate_content(prompt=final_prompt, response_schema=SummarizerOutput)
        print("Final summary generated successfully.")
        return self.parse_json_output(json_output)

    def summarize_chunks(self, text: str, prompt_name: str) -> List[str]:
        """
        Summarizes the input text by chunking it and generating intermediate summaries for each chunk.
        :param text: The input text to be summarized.
        :param prompt_name: The name of the prompt to be used for summarization.
        :return: A list of intermediate summaries for each chunk.
        """
        intermediate_summaries = []
        chunks = self.chunker.chunk(text)

        if not chunks:
            print("No chunks to process.")
            return []

        # To display progress bar
        for chunk in tqdm(chunks, desc=f"Summarizing ({prompt_name})", unit="chunk"):
            prompt = self.prompts.get(prompt_name).format(chunk=chunk)
            chunk_summary = self.model.generate_content(prompt)
            intermediate_summaries.append(chunk_summary)

        return intermediate_summaries


