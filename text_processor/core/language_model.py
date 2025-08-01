"""
This module defines the LanguageModel abstract base class and its implementations for Gemini and Ollama models.


Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

from abc import abstractmethod, ABC
import google.generativeai as genai
import ollama
from google.generativeai import GenerationConfig


from pydantic import BaseModel

class LanguageModel(ABC):

    def __init__(self, model_name: str):
        """
        Initializes the LanguageModel with an option for structured output.
        structured output, False otherwise.
        """
        self._model_name = model_name
        self.structured_output = self.compatible_with_structured_output()

    @abstractmethod
    def generate_content(self, prompt: str, response_schema: type[BaseModel] = None) -> str:
        """
        Abstract method to generate content based on a prompt and configuration.
        :param response_schema: the Pydantic model class for structured output
        :param prompt: The input prompt for content generation.
        :return: The generated text content.
        """
        pass

    def get_name(self):
        """
        Method to return the name of the model.
        """
        return self._model_name
    @abstractmethod
    def get_max_tokens(self):
        """
        Returns the maximum number of tokens the model can handle.
        This is a placeholder method and should be implemented by subclasses.
        """
    @abstractmethod
    def compatible_with_structured_output(self):
        """
        Checks if the model is compatible with structured output.
        :return: bool: True if the model supports structured output, False otherwise.
        """
        pass


class GeminiModel(LanguageModel):
    def __init__(self, api_key: str, model_name="gemini-2.0-flash"):
        """
        Initializes the GeminiModel.
        :param api_key: The API key for Google Generative AI.
        :param model_name: The name of the Gemini model to use.
        """
        genai.configure(api_key=api_key)
        super().__init__(model_name)

        self._model = genai.GenerativeModel(model_name=model_name)

    def generate_content(self, prompt, response_schema : type[BaseModel]=None) -> str:
        """
        Generates content using the configured Gemini model.
        :param prompt: Prompt for content generation.
        :param response_schema: Pydantic model class for structured output.
        :return: The generated content
        """
        gen_config = GenerationConfig()
        if response_schema:
            if self.structured_output:
                gen_config.response_schema = response_schema
                gen_config.response_mime_type = "application/json"
        response = self._model.generate_content(prompt, generation_config=gen_config)

        return response.text

    def get_name(self):
        """
        Returns the name of the Gemini model.
        """
        return self._model_name

    def get_max_tokens(self):
        """
        Returns the maximum number of tokens the Gemini model can handle.
        """
        return genai.get_model(self.get_name()).input_token_limit

    def compatible_with_structured_output(self):
        return "generateContent" in genai.get_model(self.get_name()).supported_generation_methods

class OllamaModel(LanguageModel):
    def __init__(self, model_name, ollama_base_url="http://localhost:11434"):
        """
        :param model_name: Model name
        :param ollama_base_url: url for ollama server
        """
        super().__init__(model_name)
        self._ollama_base_url = ollama_base_url


    def generate_content(self, prompt: str, response_schema: type[BaseModel]=None) -> str:
        """
        Generates content using the configured Ollama model.
        :param prompt: The input prompt for content generation.
        :param response_schema: The response_sschema for structured outputs
        :return: The generated text content.
        """

        if response_schema:
            response = ollama.generate(model=self._model_name, format=response_schema.model_json_schema(), prompt=prompt)
        else:
            response = ollama.generate(model=self._model_name, prompt=prompt)

        return response['response']

    def get_name(self):
        """
        Returns the name of the Ollama model.
        """
        return self._model_name


    def get_max_tokens(self):
        """
        Return the maximum number of tokens the Ollama model can handle.
        """
        model_info = ollama.show(self.get_name()).modelinfo
        arch_name = model_info.get("general.architecture")
        return model_info.get(f"{arch_name}.context_length")



    def compatible_with_structured_output(self):
        """
        Checks if the Ollama model is compatible with structured output.
        :return: bool: True if the model supports structured output, False otherwise.
        """
        return True
