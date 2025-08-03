import os
from pyprojroot import here


def create_directory(directory_path: str) -> None:
    """
    Create a directory if it does not exist.

    Args:
        directory_path (str): Relative path from project root to the directory.
    """
    full_path = here(directory_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
