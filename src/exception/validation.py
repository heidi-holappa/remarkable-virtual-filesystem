"""
Errors regarding data validation
"""

from src.exception.base import VFSError


class ValidationError(VFSError):
    """
    Base class for validation errors
    """

class InvalidArgumentError(ValidationError):
    """
    An exception raised if user provides an invalid argument
    """

class InvalidContentError(ValidationError):
    """
    An exception raised by failed content file validation
    """

class InvalidMetadataError(ValidationError):
    """
    An exception raised by failed metadata validation
    """

class ConstraintViolationError(ValidationError):
    """
    An exception raised if a constraint has been violated
    """
