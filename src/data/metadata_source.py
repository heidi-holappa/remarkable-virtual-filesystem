"""
    Base module for the source of metadata
"""
from typing import Dict, List, Any

from src.dto.content import Content
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

    def remote_copy(self, source_file: str,
                    metadata: Metadata, content: Content) -> None:
        """
        A public method to copy a file from host machine to
        the target machine (reMarkable).

        :param source_file: absolute path to source file to be copied
        :param metadata: a metadata entry for the file
        :param content: a content entry for the file
        :return: None
        """

        raise NotImplementedError

    @staticmethod
    def restart_xochitl() -> None:
        """
        Restarts the xochitl service on the remote reMarkable device via SSH.

        This is typically required after modifying files in the xochitl data
        directory for changes to take effect.

        :raises RemarkableOperationException: if the restart command fails
        """

        raise NotImplementedError