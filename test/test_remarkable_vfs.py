import logging
import unittest
from argparse import Namespace
from unittest.mock import MagicMock, patch

from remarkable_vfs import main_loop, init_logging, main



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


class TestMainLoopInitialization(unittest.TestCase):

    @patch("remarkable_vfs.CliUi")
    @patch("remarkable_vfs.CommandDispatcher")
    @patch("remarkable_vfs.EventBus")
    @patch("remarkable_vfs.RemarkableDataRepository")
    @patch("remarkable_vfs.RemarkableSSHMetadataSourceV2")
    @patch("remarkable_vfs.logger")
    def test_main_loop_initializes_components(
        self,
        mock_logger: MagicMock,
        mock_metadata_source: MagicMock,
        mock_repository: MagicMock,
        mock_event_bus: MagicMock,
        mock_dispatcher: MagicMock,
        mock_ui: MagicMock,
    ) -> None:
        # Act
        main_loop()

        # Assert: metadata source is initialized
        mock_metadata_source.assert_called_once_with()

        # Assert: repository receives the metadata source
        mock_repository.assert_called_once_with(
            mock_metadata_source.return_value
        )

        # Assert: event bus is initialized
        mock_event_bus.assert_called_once_with()

        # Assert: dispatcher receives the repository and event bus
        mock_dispatcher.assert_called_once_with(
            mock_repository.return_value,
            mock_event_bus.return_value,
        )

        # Assert: UI receives all required dependencies
        mock_ui.assert_called_once_with(
            mock_repository.return_value,
            mock_event_bus.return_value,
            mock_dispatcher.return_value,
        )

        # Assert: startup message is logged
        mock_logger.info.assert_called_once_with("Starting UI")

        # Assert: the command loop is started
        mock_ui.return_value.loop.assert_called_once_with()
