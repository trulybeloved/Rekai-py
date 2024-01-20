"""Utilities module"""

from datetime import datetime
import time
from loguru import logger

def get_current_timestamp() -> str:
    # Ref https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior for more info on formats
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    return timestamp

def log_process_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.success(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
        return result

    return wrapper
