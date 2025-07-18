import json
import re
from abc import ABC, abstractmethod

from common.load_config import load_yaml_config
from text_processor.core.chunker import Chunker
from text_processor.core.language_model import LanguageModel
from text_processor.core.schemas import SummarizerOutput


class Summarizer(ABC):
    def __init__(self, model: LanguageModel, chunker: Chunker, summary_length=800):
        """
        Initializes the Summarizer with a language model, chunker, and summary length.
        :param model: The language model to be used for summarization.
        :param chunker: The chunker to split the text into manageable pieces.
        :param summary_length: The maximum length of the summary to be generated.
        """
        self.model = model
        self.chunker = chunker
        self.summary_length = summary_length


    @abstractmethod
    def summarize(self, text: str) -> SummarizerOutput:
        pass

class HierarchicalSummarizer(Summarizer):
    def __init__(self, model: LanguageModel, chunker: Chunker, prompts_config_file, summary_length=800):
        """
        Initializes the HierarchicalSummarizer with a language model, chunker, prompts configuration file, and summary length.
        :param model: The language model to be used for summarization.
        :param chunker: The chunker to split the text into manageable pieces.
        :param prompts_config_file: The path to the YAML configuration file containing prompts for summarization.
        :param summary_length: The maximum length of the summary to be generated.
        """
        super().__init__(model, chunker,summary_length)
        self.prompts = load_yaml_config(prompts_config_file)


    def summarize(self, text) -> SummarizerOutput:
        """
        Summarizes the input text by first chunking it into smaller pieces, then generating intermediate summaries for each chunk,
        :param text: The input text to be summarized.
        :return: The final summary and themes extracted from the text.
        """
        intermediate_summaries = []
        chunks = self.chunker.chunk(text)
        for chunk in chunks:
            prompt = self.prompts.get("chunk_summary").format(chunk=chunk, word_limit=self.summary_length)
            chunk_summary = self.model.generate_content(prompt)
            intermediate_summaries.append(chunk_summary)
        if not intermediate_summaries:
            return SummarizerOutput(summary="", themes=[])

        else:
            combined_intermediate_summaries = "\n\n".join(intermediate_summaries)
            final_prompt = self.prompts.get("final_summary").format(
                summaries=combined_intermediate_summaries,
                word_limit=self.summary_length
            )
            json_output = self.model.generate_content(prompt=final_prompt, response_schema=SummarizerOutput)
            return parse_json_output(json_output)



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




