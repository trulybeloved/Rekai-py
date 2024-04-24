"""Utilities module"""

## built-in modules
from datetime import datetime

import os
import zipfile
import base64
import time

## third-party modules
from loguru import logger
import pandas as pd
import tiktoken

## custom modules
from appconfig import AppConfig


def get_current_timestamps() -> tuple[str, int]:
    current_time = datetime.utcnow()
    return current_time.strftime('%Y_%m_%d_%H_%M_%S'), int(current_time.timestamp())


def log_execution_time(func):
    """
    Decorator that logs the execution time of a function if AppConfig.ENABLE_TIMING is True.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    Raises:
        Exception: If the wrapped function raises an exception, it is logged along with the execution time.

    Note:
        - The AppConfig.ENABLE_TIMING flag controls whether timing information is logged.
        - The logger is expected to have 'error' and 'success' methods for logging errors and successes, respectively.
    """

    def wrapper(*args, **kwargs):
        if not AppConfig.ENABLE_TIMING:
            return func(*args, **kwargs)

        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"{func.__name__} failed with error: {str(e)}")
            logger.error(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
            raise
        else:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.success(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
            return result

    return wrapper


def zip_directory(directory_to_zip, zip_file_name: str, zip_save_directory: str):
    """
    Zip all contents in a directory and return the zip file path.

    Parameters:
    - directory_path: The path of the directory to be zipped.
    - zip_file_name: The name of the zip file to be created.

    Returns:
    - The path of the created zip file.
    """

    if not os.path.exists(directory_to_zip):
        raise FileNotFoundError(f"The directory '{directory_to_zip}' does not exist.")

    if not os.path.isdir(directory_to_zip):
        raise NotADirectoryError(f"'{directory_to_zip}' is not a directory.")

    zip_file_path = os.path.join(zip_save_directory, zip_file_name + ".zip")

    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:

        for root, _, files in os.walk(directory_to_zip):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, directory_to_zip))

    return zip_file_path

def encode_bytes_to_base64_string(input_bytes: bytes) -> str:
    encoded_data = base64.b64encode(input_bytes).decode('utf-8')
    return encoded_data

def decode_bytes_from_base64_string(input_base64: str) -> bytes:
    decoded_data = base64.b64decode(input_base64)
    return decoded_data

#OpenAI Tokenizer
def tiktoken_get_tokens_in_string(string: str, encoding_name: str = 'cl100k_base') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class ProgressMonitor:

    _instances = []
    log_path: str

    def __init__(self, task_name: str, total_task_count: int):
        if not isinstance(task_name, str) or not isinstance(total_task_count, int):
            raise ValueError(
                "Invalid input types. task_name should be a string, and total_task_count should be an integer.")

        if total_task_count <= 0:
            raise ValueError("Total task count must be greater than 0.")

        self._task_name = task_name
        self._total_task_count = total_task_count
        self._completed_task_count = 0

        ProgressMonitor._instances.append(self)

    def mark_completion(self, count: int = 1):
        if not isinstance(count, int) or count <= 0:
            raise ValueError("Invalid input type for count. It should be a positive integer.")

        self._completed_task_count += count

    def get_progress(self):
        progress_percentage = (self._completed_task_count / self._total_task_count) * 100
        return f'{self._task_name} - {self._completed_task_count}/{self._total_task_count} completed - {progress_percentage:.2f}% complete'

    def reset_progress(self):
        self._completed_task_count = 0

    def set_total_tasks(self, total_task_count: int):
        if not isinstance(total_task_count, int) or total_task_count <= 0:
            raise ValueError("Total task count must be a positive integer.")

        self._total_task_count = total_task_count

    def get_percentage_completion(self) -> int:
        return round((self._completed_task_count / self._total_task_count * 100))

    @property
    def task_name(self):
        return self._task_name

    @property
    def total_task_count(self):
        return self._total_task_count

    @property
    def completed_task_count(self):
        return self._completed_task_count

    @classmethod
    def get_all_instances(cls):
        return cls._instances

    @classmethod
    def get_progress_dataframe(cls) -> pd.DataFrame:

        instances: list[ProgressMonitor] = cls.get_all_instances()

        if instances:
            transmutors = []
            progress = []

            for instance in instances:
                transmutors.append(instance.task_name)
                progress.append(instance.get_percentage_completion())

            progress_df = pd.DataFrame(
                {
                    "Transmutor": transmutors,
                    "Progress": progress
                }
            )

            return progress_df

        else:
            return pd.DataFrame(
                {
                    "Transmutor": ["None"],
                    "Progress": [0]
                }
            )

    @classmethod
    def destroy_all_instances(cls):
        for instance in cls._instances:
            del instance
        cls._instances = []

    # def read_log(self):
    #     with open(self.log_path, 'r', encoding='utf-8') as log_file:
    #         log_text = log_file.read()
    #         return log_text

class MetaLogger:
    @staticmethod
    def log_backoff_retry(details: dict):
        logger.warning(
            "Backing off {wait:0.1f} seconds after {tries} tries "
            "calling function {target} with args {args} and kwargs "
            "{kwargs}".format(**details))

    @staticmethod
    def log_backoff_giveup(details: dict):
        logger.critical(
            "Backing off failed after {tries} tries "
            "for function {target} with args {args} and kwargs "
            "{kwargs}".format(**details))

    @staticmethod
    def log_backoff_success(details: dict):
        if AppConfig.deep_log_transmutors:
            logger.info(
                "function {target} was successful after {tries} tries "
                "for function {target} with args {args} and kwargs "
                "{kwargs}".format(**details))

    @staticmethod
    def log_exception(function: str, exception: Exception):
        logger.exception(f'The function {function} raised sn exception: {exception}')