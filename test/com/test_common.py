import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.com.common import cd, ls, mv, rm, clear
from test.stub_remarkable_metadata_source import StubRemarkableMetadataSource
from src.workspace.workspace_manager import WorkspaceManager

from test.test_data import UUID_A, UUID_D_1, UUID_ROOT, UUID_A0


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

    def test_cd_with_non_existing_path_informs_user_path_does_not_exist(self) -> None:
        self.ws.set_current_collection("")
        path: str = "/path/does/not/exist"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            cd([path], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue(f"cd: {path}: No such file or directory" in output, msg=f"Output was: {output}")

    def test_cd_to_file_informs_user_the_targer_is_not_a_directory(self) -> None:
        self.ws.set_current_collection("")
        path: str = "/A/Fairytale.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            cd([path], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue(f"cd: {path}: Not a directory" in output, msg=f"Output was: {output}")

    def test_cd_to_collection_with_a_whitespace_in_its_visble_name(self) -> None:
        self.ws.set_current_collection("")
        cd(["D 1"], self.manager)
        self.assertTrue(self.ws.get_current_collection() == UUID_D_1)

    # -------------------------------
    # ls instruction
    # -------------------------------
    def test_ls_root(self) -> None:
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("A/" in output, msg=f"Output was: {output}")
            self.assertTrue("B/" in output, msg=f"Output was: {output}")

    def test_ls_sub_path(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("A_0/" in output, msg=f"Output was: {output}")

    def test_ls_file_with_size(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_args_informs_of_usage(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls(["a"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("ls: usage: ls" in output, msg=f"Output was: {output}")

    def test_ls_full_output_for_root(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("size (kB)       name" in output, msg=f"Output was: {output}")
            self.assertTrue("                ./" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               B/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               D 1/" in output, msg=f"Output was: {output}")

    def test_ls_full_output_for_dir_with_files(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("size (kB)       name" in output, msg=f"Output was: {output}")
            self.assertTrue("                ../" in output, msg=f"Output was: {output}")
            self.assertTrue("                ./" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A_0/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A_1/" in output, msg=f"Output was: {output}")
            self.assertTrue("4096            Fairytale-2.pdf" in output, msg=f"Output was: {output}")
            self.assertTrue("1024            Fairytale.pdf" in output, msg=f"Output was: {output}")
            self.assertTrue("2048            InvalidLastModified.pdf" in output, msg=f"Output was: {output}")


    def test_ls_full_output_for_dir_without_files_or_subdirectories(self) -> None:
        self.ws.set_current_collection(UUID_A0)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls([], self.manager)
            output: str = mock_out.getvalue()
            expected_output = """size (kB)       name
                ../
                ./
"""
            self.assertEqual(expected_output, output, msg=f"Output was: {output}")


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
    def test_mv_without_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            mv([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage (mvp):" in output, msg=f"Output was: {output}")

    def test_mv_with_multiple_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            mv(["-r", "foo.pdf", "bar/"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage (mvp):" in output, msg=f"Output was: {output}")

    # -------------------------------
    # rm instruction
    # -------------------------------
    def test_rm_no_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            rm([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: rm <file or path>" in output, msg=f"Output was: {output}")

    def test_rm_too_many_args(self) -> None:
        """
        When user attempts to use mv instruction with
        multiple arguments, they are instructed of the
        usage of the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            rm(["-rf", "/foo"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: rm <file or path>" in output, msg=f"Output was: {output}")
