import copy
import unittest

from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.command.command_dispatcher import CommandDispatcher
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2

from src.exception import InvalidArgumentError

from test.test_data_v2 import TEST_DATA


class CommandDispatcherTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.dispatcher = CommandDispatcher(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus()
        )

    @patch("src.command.commands.exit.sys.exit")
    @patch.object(RemarkableDataRepository, "restart_xochitl")
    def test_happy_case_exit_command(
        self,
        mock_restart: MagicMock,
        mock_exit: MagicMock
    ) -> None:
        self.dispatcher.dispatch("x", [])

        mock_restart.assert_called_once_with()
        mock_exit.assert_called_once_with(0)


    def test_command_not_found(self) -> None:
        with self.assertRaisesRegex(
            InvalidArgumentError,
            "unknown: command not found"
        ):
            self.dispatcher.dispatch("unknown", [])
