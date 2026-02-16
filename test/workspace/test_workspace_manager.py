import unittest

from src.workspace.workspace_manager import WorkspaceManager
from src.workspace.remarkable_workspace import RemarkableWorkspace
from test.stub_remarkable_metadata_source import StubRemarkableMetadataSource


class TestWorkspaceManager(unittest.TestCase):


    def setUp(self) -> None:

        self.manager = WorkspaceManager(StubRemarkableMetadataSource())


    def test_refresh(self) -> None:
        ws: RemarkableWorkspace = self.manager.get()
        ws2: RemarkableWorkspace =self.manager.refresh()
        self.assertEqual(ws.get_data(), ws2.get_data())