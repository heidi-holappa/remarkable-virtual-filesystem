"""
    Exception to raise when provided path does not
    point to a CollectionType (directory)
"""

class NotADirectoryException(Exception):
    """
        Exception for handling paths that are expected to point
        to a directory but point to another type of entity. Currently,
        the only other type of entities are DocumentTypes (files)
    """
