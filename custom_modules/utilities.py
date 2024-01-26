"""Utilities module"""

from datetime import datetime
import time
from loguru import logger

def get_current_timestamps() -> [str, int]:
    current_time = datetime.utcnow()
    return current_time.strftime('%Y_%m_%d_%H_%M_%S'), int(current_time.timestamp())

def log_process_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.success(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
        return result

    return wrapper
