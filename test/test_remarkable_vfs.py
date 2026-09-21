import logging
import unittest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from remarkable_vfs import main_loop, init_logging, main, execute_command
from test.stub_remarkable_metadata_source_v2 import StubRemarkableMetadataSourceV2
from src.workspace.workspace_manager import WorkspaceManager


class TestMainLoop(unittest.TestCase):

    @patch("remarkable_vfs.main_loop")
    @patch("remarkable_vfs.logger")
    @patch("remarkable_vfs.init_logging")
    @patch("remarkable_vfs.init_argparse")
    def test_main(
            self,
            mock_init_argparse: MagicMock,
            mock_init_logging: MagicMock,
            mock_logger: MagicMock,
            mock_main_loop: MagicMock,
    ) -> None:
        mock_parser = MagicMock()
        mock_args = Namespace(
            log=True,
            log_level="DEBUG",
        )

        mock_init_argparse.return_value = mock_parser
        mock_parser.parse_args.return_value = mock_args

        main()

        mock_init_argparse.assert_called_once_with()
        mock_parser.parse_args.assert_called_once_with()
        mock_init_logging.assert_called_once_with(mock_args)

        mock_logger.info.assert_called_once_with(
            "Starting Remarkable VirtualFilesSystem main loop"
        )

        mock_main_loop.assert_called_once_with()

    @patch("remarkable_vfs.cd")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_cd_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_cd: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["cd foo", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_cd.assert_called_once_with(
            ["foo"],
            stubbed_workspace_manager,
        )

        mock_exit.assert_called_once_with(
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.ls")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_ls_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_ls: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = [
            "ls -la",
            "exit",
        ]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_ls.assert_called_once_with(
            ["-la"],
            stubbed_workspace_manager,
        )

        mock_exit.assert_called_once_with(
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.clear")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_clear_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_clear: MagicMock,
    ) -> None:
        self.run_command(
            "clear",
            mock_input,
            mock_workspace_manager,
        )

        mock_clear.assert_called_once_with()

    @patch("remarkable_vfs.rm")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_rm_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_rm: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["rm file.txt", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_rm.assert_called_once_with(
            ["file.txt"],
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.mv")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_mv_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_mv: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["mv old.txt new.txt", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()


        mock_mv.assert_called_once_with(
            ["old.txt", "new.txt"],
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.rcp")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_rcp_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_rcp: MagicMock,
    ) -> None:

        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["rcp source.txt destination.txt", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_rcp.assert_called_once_with(
            ["source.txt", "destination.txt"],
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.help_instruction")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_help_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_help: MagicMock,
    ) -> None:
        self.run_command(
            "help ls",
            mock_input,
            mock_workspace_manager,
        )

        mock_help.assert_called_once_with(["ls"])

    @patch("remarkable_vfs.refresh")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_refresh_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_refresh: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["refresh", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_refresh.assert_called_once_with(
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.mkdir")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_mkdir_command(
            self,
            mock_workspace_manager_getter: MagicMock,
            mock_input: MagicMock,
            mock_mkdir: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager_getter.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager_getter.get.return_value = mock_ws

        mock_input.side_effect = ["mkdir test_dir", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_mkdir.assert_called_once_with(
            ["test_dir"],
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.rename")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_rename_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_rename: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = ["rename old new", "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        mock_rename.assert_called_once_with(
            ["old", "new"],
            stubbed_workspace_manager,
        )

    @patch("remarkable_vfs.execute_command")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_exit_command(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_execute_command: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.return_value = "exit"
        mock_execute_command.return_value = False

        main_loop()

        mock_execute_command.assert_called_once_with(
            "exit",
            [],
            stubbed_workspace_manager
        )

    @patch("remarkable_vfs.handle_exit")
    def test_x_command_returns_false(self,
                                     mock_handle_exit: MagicMock) -> None:

        workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        result = execute_command("x", [], workspace_manager)

        mock_handle_exit.assert_called_once()
        self.assertFalse(result)

    @patch("remarkable_vfs.cd")
    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    def test_empty_command_is_ignored(
            self,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
            mock_cd: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = [
            "",
            "cd foo",
            "exit",
        ]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ):
            with self.assertRaises(SystemExit):
                main_loop()

        mock_cd.assert_called_once_with(
            ["foo"],
            stubbed_workspace_manager,
        )

    @patch("builtins.input")
    @patch("remarkable_vfs.get_workspace_manager")
    @patch("builtins.print")
    def test_unknown_command(
            self,
            mock_print: MagicMock,
            mock_workspace_manager: MagicMock,
            mock_input: MagicMock,
    ) -> None:
        stubbed_workspace_manager = WorkspaceManager(StubRemarkableMetadataSourceV2())
        mock_workspace_manager.return_value = stubbed_workspace_manager
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = [
            "foobar",
            "exit",
        ]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ):
            with self.assertRaises(SystemExit):
                main_loop()

        mock_print.assert_called_once_with(
            "Command 'foobar' not found.\nTry: help"
        )

    def run_command(self,
                    command: str,
                    mock_input: MagicMock,
                    mock_workspace_manager: MagicMock) -> MagicMock:
        mock_ws = MagicMock()
        mock_ws.get_current_path.return_value = "/home/test"
        mock_workspace_manager.get.return_value = mock_ws

        mock_input.side_effect = [command, "exit"]

        with patch(
                "remarkable_vfs.handle_exit",
                side_effect=SystemExit,
        ) as mock_exit:
            with self.assertRaises(SystemExit):
                main_loop()

        return mock_exit


class TestLogging(unittest.TestCase):

    @patch("remarkable_vfs.logging.basicConfig")
    @patch("remarkable_vfs.logger")
    def test_logging_enabled(self,
                             mock_logger: MagicMock,
                             mock_basic_config: MagicMock) -> None:
        args = Namespace(
            log=True,
            log_level="DEBUG",
        )

        init_logging(args)

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format="%(levelname)s:%(name)s: %(message)s",
        )

        mock_logger.info.assert_called_once_with(
            "Logging enabled. Using log level %s",
            args.log_level,
        )

    @patch("remarkable_vfs.logging.basicConfig")
    @patch("remarkable_vfs.logger")
    def test_logging_disabled(self,
                              mock_logger: MagicMock,
                              mock_basic_config: MagicMock) -> None:
        args = Namespace(
            log=False,
            log_level="DEBUG",
        )

        init_logging(args)

        mock_basic_config.assert_not_called()
        mock_logger.info.assert_not_called()

import unittest

from remarkable_vfs import init_argparse


class TestInitArgparse(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = init_argparse()

    def test_default_arguments(self) -> None:
        args = self.parser.parse_args([])

        self.assertFalse(args.log)
        self.assertEqual(args.log_level, "INFO")

    def test_log_flag(self) -> None:
        args = self.parser.parse_args(["--log"])

        self.assertTrue(args.log)
        self.assertEqual(args.log_level, "INFO")

    def test_log_level(self) -> None:
        for level in ["DEBUG", "INFO", "WARN", "ERROR"]:
            with self.subTest(level=level):
                args = self.parser.parse_args([
                    "--log-level",
                    level,
                ])

                self.assertEqual(args.log_level, level)

    def test_invalid_log_level(self) -> None:
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "--log-level",
                "INVALID",
            ])
