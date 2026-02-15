"""
    Base module for the source of metadata
"""
from typing import Dict, Any

class MetadataSource:
    """
        Base class for the source of metadata
    """

    def load(self) -> Dict[str, Dict[str, Any]]:
        """
        A public method to load metadata into memory
        :return: a dictionary of metadata
        """
        raise NotImplementedError
