"""Utilities module"""

from datetime import datetime


def get_current_timestamp() -> str:
    # Ref https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior for more info on formats
    timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    return timestamp
