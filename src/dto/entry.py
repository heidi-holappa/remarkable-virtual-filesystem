"""
module for user data entry
"""

from dataclasses import dataclass

from src.dto.content import Content
from src.dto.metadata import Metadata

@dataclass
class Entry:
    """
    A representation of all the user data that is relevant
    for the virtual filesystem
    """

    metadata: Metadata
    content: Content | None = None
    size: int | None = None
