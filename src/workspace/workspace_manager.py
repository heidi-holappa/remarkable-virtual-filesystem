"""
    Module for the workspace manager
"""

from typing import Optional

from src.data.metadata_source_v2 import MetadataSourceV2
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.workspace.remarkable_workspace_v2 import RemarkableWorkspaceV2

class WorkspaceManager:
    """
        Workspace manager manages the reMarkable workspace. At any given
        time there should exist only one workspace.

        If the workspace is to be refreshed, a new workspace is created.
    """

    def __init__(self, source: MetadataSourceV2):
        self._repository = RemarkableDataRepository(source)
        self._workspace: RemarkableWorkspaceV2 = RemarkableWorkspaceV2(self._repository)

    def get(self) -> RemarkableWorkspaceV2:
        """
        Either created a new workspace or returns an existing
        instance of the workspace

        :return: an instance of the reMarkable workspace
        """
        return self._workspace

    def refresh(self) -> RemarkableWorkspaceV2:
        """
        Creates a new instance of the reMarkable workspace replacing
        the previous instance, if one exists.

        :return: an instance of reMarkable workspace
        """
        self._workspace = RemarkableWorkspaceV2(self._repository)
        return self._workspace

