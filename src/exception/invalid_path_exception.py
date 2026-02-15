"""
    Exception for handling invalid paths
"""

class InvalidPathException(Exception):
    """
        Exception for handling invalid paths. An invalid path
        may occur due to user input, such as user using cd
        instruction with a path that does not exist.
    """
