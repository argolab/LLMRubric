"""
Author: Prabhav Singh
Implementation of: LLMRubric (https://aclanthology.org/2024.acl-long.745v2.pdf)

Utils:
- CacheManager: Manages API response caching to avoid redundant requests.
- EvaluationResult: Formats and stores evaluation results with timestamps.
"""

from typing import Dict, List, Union, Optional
import json
import hashlib
import pickle
import os
from src.config import Config
from datetime import datetime, timedelta
from datetime import datetime

class CacheManager:
    """
    Handles caching of API responses to improve efficiency and reduce redundant calls.

    Caching is based on:
    - The input prompt.
    - Model settings (model name, temperature, max retries).
    - A unique hash of the rubric to track version changes.

    Attributes:
        cache_dir (str): Directory where cache files are stored.
        config (Config): Model configuration parameters.
        rubric_hash (str): Hash of the rubric to detect version changes.
    """

    def __init__(self, cache_dir: str, config: Config, rubric: dict):
        """
        Initializes the cache manager.

        Args:
            cache_dir (str): Directory to store cache files.
            config (Config): Configuration settings for the model.
            rubric (dict): The rubric dictionary used for evaluation.
        """
        self.cache_dir = cache_dir
        self.config = config
        self.rubric_hash = self._get_rubric_hash(rubric)
        os.makedirs(cache_dir, exist_ok=True)

    def _get_rubric_hash(self, rubric: dict) -> str:
        """
        Generates a hash of the rubric to track changes across different versions.

        Args:
            rubric (dict): The rubric content.

        Returns:
            str: MD5 hash of the rubric.
        """
        rubric_json = json.dumps(rubric, sort_keys=True)  # Ensure consistent ordering
        return hashlib.md5(rubric_json.encode()).hexdigest()

    def _get_cache_key(self, prompt: str, model: str, temperature: float) -> str:
        """
        Generates a unique cache key using the prompt, model settings, and rubric hash.

        Args:
            prompt (str): The input prompt for LLM evaluation.
            model (str): Name of OpenAI Model.
            temperature (str): Temperature of sampling.

        Returns:
            str: MD5 hash representing the unique cache key.
        """
        config_str = f"{model}-{temperature}-{self.config.max_retries}"
        key_string = f"{prompt}-{config_str}-{self.rubric_hash}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_cache_expired(self, cache_file: str) -> bool:
        """
        Checks if a cached file has expired based on the configured expiration time.

        Args:
            cache_file (str): The full path to the cache file.

        Returns:
            bool: True if the cache file is expired, False otherwise.
        """
        expiry_time = timedelta(days=self.config.cache_expiry_days)
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        return datetime.now() - file_modified_time > expiry_time

    def get(self, prompt: str, model: str, temperature: str) -> Optional[List[float]]:
        """
        Retrieves a cached result if available and not expired.

        Args:
            prompt (str): The input prompt.
            model (str): Name of OpenAI Model.
            temperature (str): Temperature of sampling.

        Returns:
            Optional[List[float]]: Cached probabilities if available and valid, else None.
        """

        cache_key = self._get_cache_key(prompt, model, temperature)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        if os.path.exists(cache_file):
            if self._is_cache_expired(cache_file):
                os.remove(cache_file)
                return None
            with open(cache_file, "rb") as f:
                return pickle.load(f)
            
        return None

    def set(self, prompt: str, model: str, temperature: float, result: List[float]) -> None:
        """
        Stores the result in cache for future reuse.

        Args:
            prompt (str): The input prompt.
            result (List[float]): The probability distribution to be cached.
            model (str): Name of OpenAI Model.
            temperature (str): Temperature of sampling.
        """
        cache_key = self._get_cache_key(prompt, model, temperature)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")

        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        

class EvaluationResult:
    """
    Stores and manages evaluation results.

    Attributes:
        results (Dict[str, List[float]]): Stores probability distributions for each question.
        timestamps (Dict[str, datetime]): Timestamps when results were recorded.
        model (str): Name of OpenAI Model.
        temperature (str): Temperature of sampling.
    """

    def __init__(self):
        """
        Initializes an empty evaluation result container.
        """

        self.results: Dict[str, List[float]] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.model: str = None
        self.temperature: float = None

    def add_result(self, question_id: str, probabilities: List[float]) -> None:
        """
        Adds a result for a given question.

        Args:
            question_id (str): The question identifier.
            probabilities (List[float]): Probability distribution for the given question.
        """
        self.results[question_id] = probabilities
        self.timestamps[question_id] = datetime.now()

    def to_dict(self) -> Dict:
        """
        Converts results into a dictionary format.

        Returns:
            Dict: A dictionary containing results and timestamps.
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "results": self.results,
            "timestamps": {k: v.isoformat() for k, v in self.timestamps.items()}
        }


    def save(self, filepath: str, data: List[Dict]) -> None:
        """
        Saves results to a JSON file.

        Args:
            filepath (str): The file path to save the results.
        """
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)