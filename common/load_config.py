
"""
This module provides functionality to load a YAML configuration file.

Author: Rachel Tranchida
Date: July 23, 2025
Version: 1.0.0
"""

import yaml
import os


def load_yaml_config(filepath: str) -> dict:
    """
    Loads a YAML configuration file and returns its content as a dictionary.
    :param filepath:  Path to the YAML file.
    :return: A dictionary containing the configuration data, or None if an error occurs.
    """
    if not os.path.exists(filepath):
       raise FileNotFoundError(f"File {filepath} does not exist.")

    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except yaml.YAMLError as exc:
        raise yaml.YAMLError(f"Error parsing YAML file {filepath}: {exc}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred while loading the YAML file {filepath}: {e}")