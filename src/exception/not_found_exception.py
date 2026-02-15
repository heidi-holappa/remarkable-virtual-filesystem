"""
    Exception for handling invalid UUID keys
"""


class NotFoundException(Exception):
    """
        An exception indicating that an entity was not found with
        the provided UUID.

        This exception signals undesired behavior in the program
        code and is most likely a symptom of a defect.
    """
