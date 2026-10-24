import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    RemarkableOperationError
)
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.exit import ExitCommand
from test.test_data_v2 import (
    TEST_DATA)


class ExitCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.exit = ExitCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))


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

        with patch("sys.stdout", new=StringIO()) as fake_out:
            with self.assertRaises(SystemExit) as context:
                self.exit.handle([])

            self.assertEqual(context.exception.code, 1)

            output = fake_out.getvalue()
            self.assertIn("failure", output)

        mock_restart_xochitl.assert_called_once()