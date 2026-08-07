"""
Provides indirect access to errors for convenience.
A bit of controversial implementation approach, but
mentioned as one valid approach in PEP 0008, "Public
and internal interfaces"
"""

from .base import VFSError
from .filesystem import *
from .remarkable import *
from .validation import *
