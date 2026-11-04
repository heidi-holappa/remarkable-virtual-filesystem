import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
from src.event.event_bus import EventBus
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.command.commands.help import HelpCommand
from src.event.event import OutputCommandMessage, OutputMessage

from test.test_data_v2 import (
    TEST_DATA)


class TestHelpInstruction(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self._help = HelpCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())

    def test_help_method_prints_to_console(self) -> None:
        with patch.object(self._help._event_bus, "publish") as mock_publish:
            self._help.handle([])
            mock_publish.assert_any_call(OutputMessage("help: show help texts"))

    def test_help_with_command_as_arg(self) -> None:
        with patch.object(self._help._event_bus, "publish") as mock_publish:
            self._help.handle(["mv"])
            mock_publish.assert_any_call(OutputMessage("mv: move entities to another collection"))



    def test_help_with_command__with_additional_info(self) -> None:
        with patch.object(self._help._event_bus, "publish") as mock_publish:
            self._help.handle(["mkdir"])
            mock_publish.assert_any_call(OutputMessage("mkdir: make new directory"))

    def test_help_command_not_found(self) -> None:
        with patch.object(self._help._event_bus, "publish") as mock_publish:
            self._help.handle(["grep"])
            mock_publish.assert_any_call(
                OutputCommandMessage(
                    "help",
                    "command not found: supported commands:"
                )
            )

    def test_help_with_invalid_number_of_args(self) -> None:
        with patch.object(self._help._event_bus, "publish") as mock_publish:
            self._help.handle(["one", "two"])
            mock_publish.assert_called_once_with(
                OutputCommandMessage(
                    "help",
                    "usage: help or help <command>"
                )
            )


