import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.event.event import OutputCommandMessage
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository

from src.exception import RemarkableOperationError
from src.command.commands.refresh import RefreshCommand
from test.test_data_v2 import (TEST_DATA)


class RefreshCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.refresh = RefreshCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())

    # -------------------------------
    # refresh instruction
    # -------------------------------
    @patch.object(RemarkableDataRepository, "restart_xochitl")
    def test_refresh_positive_case(self, mock_restart_xochitl: MagicMock) -> None:
        self.refresh.handle([])
        mock_restart_xochitl.assert_called_once()

    @patch.object(RemarkableDataRepository, "restart_xochitl")
    def test_refresh_logs_exception(self, mock_restart_xochitl: MagicMock) -> None:
        mock_restart_xochitl.side_effect = RemarkableOperationError("failure")

        with patch.object(self.refresh._event_bus, "publish") as mock_publish:
            self.refresh.handle([])
            mock_publish.assert_called_once_with(
                OutputCommandMessage(
                    "refresh",
                    "unexpected error occurred: failure"
                )
            )

        mock_restart_xochitl.assert_called_once()