import unittest

from test.test_data import TEST_DATA

from src.com.common import cd, ls, mv, rm, clear
from test.stub_remarkable_metadata_source import StubRemarkableMetadataSource
from src.workspace.workspace_manager import WorkspaceManager
from src.workspace.remarkable_workspace import RemarkableWorkspace

class TestCommon(unittest.TestCase):

    def setUp(self) -> None:
        # In python overriding private attributes is possible. Here
        # we abuse this capability to set the test data to the workspace

        self.manager = WorkspaceManager(StubRemarkableMetadataSource())
        self.ws = self.manager.get()

    def test_cd_without_args_sets_current_path_to_root(self) -> None:
        self.ws.set_current_collection("a")
        cd([], self.manager)
        self.assertTrue(self.ws.get_current_collection() == "")

    def test_cd_to_subpath_works(self) -> None:
        """
        Verifies that changing collection to a direct subcollection
        works. The intention is to verify that all paths in cd-method
        work as intended.

        Note: Change directory is tested more comprehensively in
        RemarkableWorkspace test suite
        :return: None
        """
        self.ws.set_current_collection("")
        cd(["A"], self.manager)
        self.assertTrue(self.ws.get_current_collection() == "a")

