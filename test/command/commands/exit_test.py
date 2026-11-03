import copy
import unittest
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    RemarkableOperationError,
    InvalidArgumentError
)
from src.event.event import OutputCommandMessage
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.exit import ExitCommand
from test.test_data_v2 import (
    TEST_DATA)


class ExitCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.exit = ExitCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())


    # -------------------------------
    # exit instruction
    # -------------------------------
    @patch.object(RemarkableDataRepository, "restart_xochitl")
    def test_handle_exit_success(self, mock_restart_xochitl: MagicMock) -> None:
        mock_restart_xochitl.return_value = None

        with self.assertRaises(SystemExit) as context:
            self.exit.handle([])

        self.assertEqual(context.exception.code, 0)
        mock_restart_xochitl.assert_called_once()

    @patch.object(RemarkableDataRepository, "restart_xochitl")
    def test_handle_exit_failure(self, mock_restart_xochitl: MagicMock) -> None:
        # Arrange
        mock_restart_xochitl.side_effect = RemarkableOperationError("failure")

        with patch.object(self.exit._event_bus, "publish") as mock_publish:
            with self.assertRaises(SystemExit) as context:
                self.exit.handle([])

            self.assertEqual(context.exception.code, 1)

            mock_publish.assert_called_once_with(
                OutputCommandMessage(
                    "exit",
                    "failure"
                )

            )

        mock_restart_xochitl.assert_called_once()

    def test_handle_exit_invalid_argument(self) -> None:
        with self.assertRaises(InvalidArgumentError) as ctx:
            self.exit.handle(["unsupported_arg"])

        self.assertTrue("exit: command does not support args" in str(ctx.exception))
