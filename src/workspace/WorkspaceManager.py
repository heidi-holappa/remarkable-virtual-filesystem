from typing import Optional

from src.data import MetadataSource
from src.workspace.RemarkableWorkspace import RemarkableWorkspace

class WorkspaceManager:

    def __init__(self, source: MetadataSource):
        self._source = source
        self._workspace: Optional[RemarkableWorkspace] = None

    def get(self) -> RemarkableWorkspace:
        if self._workspace in None:
            self._workspace = RemarkableWorkspace(self._source.load())
        return self._workspace

    def refresh(self) -> RemarkableWorkspace:
        self._workspace = RemarkableWorkspace(self._source.load())
        return self._workspace
