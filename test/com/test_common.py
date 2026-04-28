import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.com.common import cd, ls, mv, rm, mkdir, rcp, clear, refresh, handle_exit
from src.exception.remarkable_operation_exception import RemarkableOperationException
from src.workspace.remarkable_workspace import RemarkableWorkspace
from test.stub_remarkable_metadata_source import StubRemarkableMetadataSource
from src.workspace.workspace_manager import WorkspaceManager

from test.test_data import UUID_A, UUID_D_1, UUID_ROOT, UUID_A0, UUID_B

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

    def test_ls_with_too_many_args_informs_of_usage(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls(["a", "b"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("ls: usage: ls" in output, msg=f"Output was: {output}")

    def test_ls_with_valid_absolute_path_as_arg_lists_files_in_path(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls(["A"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_valid_relative_path_as_arg_lists_files_in_path(self) -> None:
        self.ws.set_current_collection(UUID_B)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls(["../A"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_invalid_path_informs_user_path_not_found(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            ls(["path-does-not-exist"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("ls: no such path" in output, msg=f"Output was: {output}")

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

    @patch.object(RemarkableWorkspace, "process_move_command")
    def test_mv_positive_case(self, mock_move: MagicMock) -> None:
        source = "file.txt"
        target = "./foo"
        mv([source, target], self.manager)

        mock_move.assert_called_once()

        args, _ = mock_move.call_args
        self.assertEqual(args[0], source)
        self.assertEqual(args[1], target)

    # -------------------------------
    # mkdir instruction
    # -------------------------------
    def test_mkdir_with_multiple_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            mkdir(["-r", "foo.pdf", "bar/"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: usage: mkdir <path>" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableWorkspace, "process_mkdir")
    def test_mkdir_positive_case(self, mock_mkdir: MagicMock) -> None:
        path = "foo"
        mkdir([path], self.manager)

        mock_mkdir.assert_called_once()

        args, _ = mock_mkdir.call_args
        self.assertEqual(args[0], path)


    # -------------------------------
    # rcp instruction
    # -------------------------------
    def test_rcp_without_args(self) -> None:
        """
        When user attempts to use rcp instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            rcp([], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("rcp: usage:" in output, msg=f"Output was: {output}")

    def test_rcp_with_too_many_args(self) -> None:
        """
        When user attempts to use rcp instruction with
        too many arguments, they are instructed of the
        usage of the command
        """
        self.ws.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            rcp(["-r", "/path/to/foo.pdf", "bar/"], self.manager)
            output: str = mock_out.getvalue()
            self.assertTrue("rcp: usage:" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableWorkspace, "process_rcp_command")
    def test_rcp_positive_case(self, mock_rcp: MagicMock) -> None:
        source = "path/to/file.txt"
        target = "./foo"
        rcp([source, target], self.manager)

        mock_rcp.assert_called_once()

        args, _ = mock_rcp.call_args
        self.assertEqual(args[0], source)
        self.assertEqual(args[1], target)

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

    @patch.object(RemarkableWorkspace, "process_remove_command")
    def test_rm_positive_case(self, mock_remove: MagicMock) -> None:
        file_to_remove = "file.txt"
        rm([file_to_remove], self.manager)

        mock_remove.assert_called_once()

        args, _ = mock_remove.call_args
        self.assertEqual(args[0], file_to_remove)



    # -------------------------------
    # refresh instruction
    # -------------------------------
    @patch.object(RemarkableWorkspace, "restart_xochitl")
    def test_refresh_positive_case(self, mock_restart_xochitl: MagicMock) -> None:
        refresh(self.manager)
        mock_restart_xochitl.assert_called_once()

    @patch.object(RemarkableWorkspace, "restart_xochitl")
    def test_refresh_logs_exception(self, mock_restart_xochitl: MagicMock) -> None:
        mock_restart_xochitl.side_effect = RemarkableOperationException("failure")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            refresh(self.manager)
            output = fake_out.getvalue()
            self.assertIn("refresh: unexpected error occurred", output)

        mock_restart_xochitl.assert_called_once()

    # -------------------------------
    # exit instruction
    # -------------------------------
    @patch.object(RemarkableWorkspace, "restart_xochitl")
    def test_handle_exit_success(self, mock_restart_xochitl: MagicMock) -> None:
        mock_restart_xochitl.return_value = None

        with self.assertRaises(SystemExit) as context:
            handle_exit(self.manager)

        self.assertEqual(context.exception.code, 0)
        mock_restart_xochitl.assert_called_once()

    @patch.object(RemarkableWorkspace, "restart_xochitl")
    def test_handle_exit_failure(self, mock_restart_xochitl: MagicMock) -> None:
        # Arrange
        mock_restart_xochitl.side_effect = RemarkableOperationException("failure")

        with patch("sys.stdout", new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as context:
                handle_exit(self.manager)

            self.assertEqual(context.exception.code, 1)

            output = fake_out.getvalue()
            self.assertIn("failure", output)

        mock_restart_xochitl.assert_called_once()