import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    NotFoundError
)
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.ls import ListCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_A, UUID_A0, UUID_A1,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2)


class ListCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ls = ListCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    # -----------------------
    # process ls command
    # -----------------------

    def test_ls_happy_path_returns_correct_listing(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle(args=[])
            output: str = mock_out.getvalue()

            in_memory_data = self.ls._repository.get_data()

            self.assertTrue('..' in output,
                            msg=f"Output was: {output}")
            self.assertTrue(in_memory_data[UUID_FAIRYTALE].metadata.visible_name in output,
                            msg=f"Output was: {output}")
            self.assertTrue(in_memory_data[UUID_FAIRYTALE_2].metadata.visible_name in output,
                            msg=f"Output was: {output}")
            self.assertTrue(in_memory_data[UUID_A0].metadata.visible_name in output,
                            msg=f"Output was: {output}")
            self.assertTrue(in_memory_data[UUID_A1].metadata.visible_name in output,
                            msg=f"Output was: {output}")

    def test_ls_raises_when_collection_not_found(self) -> None:
        with self.assertRaises(NotFoundError) as ctx:
            self.ls.handle(["/not-found/"])

        self.assertTrue("ls: no such path" in str(ctx.exception))

    # -------------------
    # _traverse_path
    # -------------------
    def test_traverse_path_breaks_when_collection_pointer_is_not_string(self) -> None:
        # This should not happen, but we confirm this defensive check works
        with patch.object(
                self.ls._repository,
                "_current_collection",
                None,
        ):
            result = self.ls._traverse_path("foo")

        self.assertEqual(result, None)
