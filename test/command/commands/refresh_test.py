import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
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

        with patch("sys.stdout", new=StringIO()) as fake_out:
            self.refresh.handle([])
            output = fake_out.getvalue()
            self.assertIn("refresh: unexpected error occurred", output)

        mock_restart_xochitl.assert_called_once()