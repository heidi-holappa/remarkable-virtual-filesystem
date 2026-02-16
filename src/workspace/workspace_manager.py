"""
    Module for the workspace manager
"""

from typing import Optional

from src.data.metadata_source import MetadataSource
from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource
from src.workspace.remarkable_workspace import RemarkableWorkspace

class WorkspaceManager:
    """
        Workspace manager manages the reMarkable workspace. At any given
        time there should exist only one workspace.

        If the workspace is to be refreshed, a new workspace is created.
    """

    def __init__(self, source: MetadataSource):
        self._source = source
        self._workspace: Optional[RemarkableWorkspace] = None

    def get(self) -> RemarkableWorkspace:
        """
        Either created a new workspace or returns an existing
        instance of the workspace

        :return: an instance of the reMarkable workspace
        """
        if self._workspace is None:
            self._workspace = RemarkableWorkspace(self._source.load())
        return self._workspace

    def refresh(self) -> RemarkableWorkspace:
        """
        Creates a new instance of the reMarkable workspace replacing
        the previous instance, if one exists.

        :return: an instance of reMarkable workspace
        """
        self._workspace = RemarkableWorkspace(self._source.load())
        return self._workspace


default_workspace_manager = WorkspaceManager(RemarkableSSHMetadataSource())