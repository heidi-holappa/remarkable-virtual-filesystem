import unittest

from src.workspace.workspace_manager import WorkspaceManager
from src.workspace.remarkable_workspace_v2 import RemarkableWorkspaceV2
from test.stub_remarkable_metadata_source_v2 import StubRemarkableMetadataSourceV2


class TestWorkspaceManager(unittest.TestCase):


    def setUp(self) -> None:

        self.manager = WorkspaceManager(StubRemarkableMetadataSourceV2())


    def test_refresh(self) -> None:
        ws: RemarkableWorkspaceV2 = self.manager.get()
        ws2: RemarkableWorkspaceV2 =self.manager.refresh()
        self.assertEqual(ws._repository.get_data(), ws2._repository.get_data())