"""
Errors related to interactions with reMarkable device
"""

from src.exception.base import VFSError

class RemarkableError(VFSError):
    """
    Base class for errors related to interaction
    with the reMarkable device
    """

class RemarkableOperationError(RemarkableError):
    """
    An exception representing a failure during a non-specified
    reMarkable operation.
    """

class RemarkableWriteError(RemarkableOperationError):
    """
    An exception representing a failure during a reMarkable
    write operation.
    """