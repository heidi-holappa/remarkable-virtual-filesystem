import copy
import unittest
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.clear import ClearCommand
from test.test_data_v2 import (TEST_DATA)


class ClearCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.clear = ClearCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())


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
        self.clear.handle([])
        mock_run.assert_called_once_with("clear", check=False)