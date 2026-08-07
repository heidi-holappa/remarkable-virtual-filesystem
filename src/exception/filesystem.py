"""
Errors regarding interactions with file system
"""

from src.exception.base import VFSError

class FilesystemError(VFSError):
    """
    Base class for file system errors
    """

class NotFoundError(FilesystemError):
    """
    An exception indicating that an entity was not found with
    the provided UUID.

    This exception signals undesired behavior in the program
    code and is most likely a symptom of a defect.
    """

class InvalidPathError(FilesystemError):
    """
    Exception for handling invalid paths. An invalid path
    may occur due to user input, such as user using cd
    instruction with a path that does not exist.
    """


class NoSuchFileOrDirectoryError(FilesystemError):
    """
    Exception indicating that no metadata file
    with given path exists. This includes both
    DocumentTypes (files) and CollectionTypes
    (paths).
    """

class NoSuchDirectoryError(FilesystemError):
    """
    Exception for handling paths that are expected to point
    to a directory but point to another type of entity. Currently,
    the only other type of entities are DocumentTypes (files)
    """
