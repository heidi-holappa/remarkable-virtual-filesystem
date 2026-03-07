"""
    Base module for the source of metadata
"""
from typing import Dict, List, Any

from src.dto.metadata import Metadata

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


    def refresh(self) -> None:
        """
        Restarts the reMarkable UI-application.
        Any changes made to metadata on reMarkable
        are only visible on the device after the
        application is restarted.

        :return: None
        """
        raise NotImplementedError


    def write(self, entry_uuid: str, metadata: Metadata) -> None:
        """
        A public method to write a metadata entry
        into reMarkable. If an entry with the same
        UUID exists in the device, it will be
        overwritten.

        :return: None
        """
        raise NotImplementedError

    def remove(self, entry_uuids: List[str]) -> None:
        """
        A public method to remove all files and
        files and folders from the reMarkable device
        matching any of the provided UUIDs

        :param entry_uuids: a list of UUIDs
        :return: None
        """
        raise NotImplementedError
