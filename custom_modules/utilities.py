"""Utilities module"""

import os
import zipfile
import base64
from datetime import datetime
import time
from loguru import logger

from appconfig import AppConfig


def get_current_timestamps() -> [str, int]:
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


class ProgressMonitor:

    task_name: str
    completed_task_count: int
    total_task_count: int

    def __init__(self, task_name: str, total_task_count: int):
        self.task_name = task_name
        self.total_task_count = total_task_count
        self.completed_task_count = 0

    def mark_completion(self):
        self.completed_task_count += 1

    def get_progress(self):
        return f'{self.task_name} completed for {self.completed_task_count}/{self.total_task_count} strings - {self.completed_task_count / self.total_task_count * 100}% complete'