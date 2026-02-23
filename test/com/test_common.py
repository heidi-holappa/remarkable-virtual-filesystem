import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.com.common import cd, ls, mv, rm, clear
from test.stub_remarkable_metadata_source import StubRemarkableMetadataSource
from src.workspace.workspace_manager import WorkspaceManager

from test.test_data import UUID_A

class TestCommon(unittest.TestCase):

    def setUp(self) -> None:
        # In python overriding private attributes is possible. Here
        # we abuse this capability to set the test data to the workspace

        self.manager = WorkspaceManager(StubRemarkableMetadataSource())
        self.ws = self.manager.get()

    # -------------------------------
    # cd instruction
    # -------------------------------
    def test_cd_without_args_sets_current_path_to_root(self) -> None:
        self.ws.set_current_collection(UUID_A)
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
        self.assertTrue(self.ws.get_current_collection() == UUID_A)


    def test_cd_with_too_many_args(self) -> None:
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            cd(["arg1", "arg2"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: cd OR cd <path>" in output, msg=f"Output was: {output}")

    # -------------------------------
    # ls instruction
    # -------------------------------
    def test_ls_root(self) -> None:
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("/A" in output, msg=f"Output was: {output}")
            self.assertTrue("/B" in output, msg=f"Output was: {output}")

    def test_ls_sub_path(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("/A_0" in output, msg=f"Output was: {output}")

    def test_ls_file_with_size(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("1024 kB" in output, msg=f"Output was: {output}")
            self.assertTrue("/A/Fairytale.pdf" in output, msg=f"Output was: {output}")

    # -------------------------------
    # clear instruction
    # -------------------------------
    @patch("src.com.common.subprocess.run")
    def test_clear(self, mock_run: MagicMock) -> None:
        """
        Verifies that clear() invokes subprocess.run with "clear".

        mock_run is the MagicMock injected by unittest.mock.patch,
        replacing src.com.common.subprocess.run.

        refrence: https://docs.python.org/3/library/unittest.mock.html
        """
        clear()
        mock_run.assert_called_once_with("clear", check=False)

    # -------------------------------
    # mv instruction
    # -------------------------------
    def test_mv(self) -> None:
        """
        Move instruction is not yet implemented. This test will
        break when the implementation occurs. A useful remainder
        to update tests.
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            mv([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage (mvp):" in output, msg=f"Output was: {output}")

    # -------------------------------
    # rm instruction
    # -------------------------------
    def test_rm(self) -> None:
        """
        Move instruction is not yet implemented. This test will
        break when the implementation occurs. A useful remainder
        to update tests.
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            rm([])
            output: str = mock_out.getvalue()
            self.assertTrue("Remove not implemented." in output, msg=f"Output was: {output}")