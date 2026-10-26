"""Tests for the CLI UI implementation."""

import copy
import unittest
from unittest.mock import MagicMock, Mock, call, patch

from src.command.command_dispatcher import CommandDispatcher
from src.event.event import Event, OutputMessage, ProgressUpdate
from src.ui.ui_cli import CliUi

from test.test_data_v2 import TEST_DATA

from src.event.event_bus import EventBus
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2


class TestCliUi(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)

        self.event_bus = EventBus()
        self.repository = RemarkableDataRepository(
            RemarkableSSHMetadataSourceV2()
        )
        self._dispatcher = CommandDispatcher(
            self.repository,
            self.event_bus,
        )
        self.ui = CliUi(
            self.repository,
            self.event_bus,
            self._dispatcher,
        )

    # Command parsing

    def test_parse_command(self) -> None:
        test_cases = [
            ("ls", ("ls", [])),
            ("cd documents", ("cd", ["documents"])),
            ("cp file1 file2", ("cp", ["file1", "file2"])),
            ("rm file1", ("rm", ["file1"])),
            ("rcp source target", ("rcp", ["source", "target"])),
            ("ls documents", ("ls", ["documents"])),
            ("", None),
            ("   ", None),
            ("\t\n", None),
        ]

        for line, expected in test_cases:
            with self.subTest(line=line):
                self.assertEqual(
                    CliUi._parse_command(line),
                    expected,
                )

    def test_parse_command_with_escaped_quotes(self) -> None:
        result = CliUi._parse_command(
            r'echo "say \"hello\""'
        )

        self.assertEqual(
            result,
            ("echo", ['say "hello"']),
        )

    def test_parse_command_with_unclosed_quote_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            CliUi._parse_command('open "my document.pdf')

    # Event rendering

    def test_render_output_message(self) -> None:
        event = OutputMessage(
            command="list",
            message="Found 3 files",
        )

        with patch("builtins.print") as mock_print:
            self.ui.render_event(event)

        mock_print.assert_called_once_with(
            "list: Found 3 files"
        )

    def test_render_progress_update(self) -> None:
        event = ProgressUpdate(
            command="download",
            message="Downloading",
            current=3,
            total=10,
        )

        with patch("builtins.print") as mock_print:
            self.ui.render_event(event)

        mock_print.assert_called_once_with(
            "download: Downloading: 3/10"
        )

    def test_render_unknown_event_does_nothing(self) -> None:
        event = Mock(spec=Event)

        with patch("builtins.print") as mock_print:
            self.ui.render_event(event)

        mock_print.assert_not_called()

    def test_event_bus_delivers_output_message_to_ui(self) -> None:
        event = OutputMessage(
            command="test",
            message="Hello",
        )

        with patch("builtins.print") as mock_print:
            self.event_bus.publish(event)

        mock_print.assert_called_once_with("test: Hello")

    # Main loop

    def test_loop_dispatches_command(self) -> None:
        current_path = self.repository.get_current_path()

        with patch(
                "builtins.input",
                side_effect=["help", KeyboardInterrupt],
        ) as mock_input:
            with patch("builtins.print"):
                with self.assertRaises(KeyboardInterrupt):
                    self.ui.loop()

        self.assertEqual(
            mock_input.call_args_list,
            [
                call(f"remarkable~{current_path}$ "),
                call(f"remarkable~{current_path}$ "),
            ],
        )

    def test_loop_ignores_empty_input(self) -> None:
        with patch(
            "builtins.input",
            side_effect=["", "   ", KeyboardInterrupt],
        ) as mock_input:
            with patch("builtins.print"):
                with self.assertRaises(KeyboardInterrupt):
                    self.ui.loop()

        self.assertEqual(mock_input.call_count, 3)

    def test_loop_dispatches_multiple_commands(self) -> None:
        current_path = self.repository.get_current_path()

        with patch(
            "builtins.input",
            side_effect=["help", "help", KeyboardInterrupt],
        ) as mock_input:
            with patch("builtins.print"):
                with self.assertRaises(KeyboardInterrupt):
                    self.ui.loop()

        self.assertEqual(mock_input.call_count, 3)

        self.assertEqual(
            mock_input.call_args_list,
            [
                call(f"remarkable~{current_path}$ "),
                call(f"remarkable~{current_path}$ "),
                call(f"remarkable~{current_path}$ "),
            ],
        )

    def test_loop_dispatches_real_command(self) -> None:
        """Verify a real command is dispatched through the application."""

        with patch(
            "builtins.input",
            side_effect=["help", KeyboardInterrupt],
        ):
            with patch("builtins.print") as mock_print:
                with self.assertRaises(KeyboardInterrupt):
                    self.ui.loop()

        # The real dispatcher and event bus should produce terminal output
        # if the help command publishes an OutputMessage.
        self.assertTrue(
            mock_print.called,
            "Expected the real command to produce terminal output.",
        )
