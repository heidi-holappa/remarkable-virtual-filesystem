"""
module for supported filetypes
"""

from enum import StrEnum

class FileType(StrEnum):
    """
    Document file types supported by the
    virtual filesystem
    """
    PDF = "pdf"
    EPUB = "epub"
