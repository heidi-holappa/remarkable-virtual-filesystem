"""
    Exception to use when no metadata entry matches given path
"""

class NoSuchFileOrDirectoryException(Exception):
    """
        Exception indicating that no metadata file
        with given path exists. This includes both
        DocumentTypes (files) and CollectionTypes
        (paths).
    """
