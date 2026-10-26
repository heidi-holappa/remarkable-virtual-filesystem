import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2

from src.event.event_bus import EventBus
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands import RemoveCommand 
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2)

class RemoveCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.rm = RemoveCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())
        
        
    # -------------------------------
    # rm instruction
    # -------------------------------
    def test_rm_no_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.rm._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rm.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: rm <file or path>" in output, msg=f"Output was: {output}")

    def test_rm_too_many_args(self) -> None:
        """
        When user attempts to use mv instruction with
        multiple arguments, they are instructed of the
        usage of the command
        """
        self.rm._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rm.handle(["-rf", "/foo"])
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: rm <file or path>" in output, msg=f"Output was: {output}")

    @patch.object(RemoveCommand, "_process_remove_command")
    def test_rm_positive_case(self, mock_remove: MagicMock) -> None:
        file_to_remove = "file.txt"
        self.rm.handle([file_to_remove])

        mock_remove.assert_called_once()

        _, kwargs = mock_remove.call_args
        self.assertEqual(kwargs['target_pattern'], file_to_remove)

# -------------------------------------
    # Process remove instruction
    # -------------------------------------

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_one_document_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.rm._repository.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.rm._repository.get_data())
        self.rm._process_remove_command(target_pattern="Fairytale.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.rm._repository.get_data().get(UUID_FAIRYTALE))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = [UUID_FAIRYTALE]
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_two_documents_with_wildcard_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.rm._repository.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.rm._repository.get_data())
        self.assertIn(UUID_FAIRYTALE_2, self.rm._repository.get_data())
        self.rm._process_remove_command(target_pattern="Fairytale*.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.rm._repository.get_data().get(UUID_FAIRYTALE))
        self.assertIsNone(self.rm._repository.get_data().get(UUID_FAIRYTALE_2))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = sorted([UUID_FAIRYTALE, UUID_FAIRYTALE_2])
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_collection_recursively(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.rm._repository.set_current_collection(UUID_ROOT)

        expected_removals: set[str] = {
            UUID_A, UUID_A0, UUID_A1,
            UUID_FAIRYTALE,
            UUID_FAIRYTALE_2
        }
        self.assertTrue(expected_removals.issubset(self.rm._repository.get_data()))

        self.rm._process_remove_command(target_pattern="A")
        self.assertEqual(mock_remove.call_count, 1)

        args, kwargs = mock_remove.call_args
        passed_list = args[0]

        self.assertEqual(sorted(expected_removals), sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_target_not_found(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.rm._repository.set_current_collection(UUID_A)

        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rm._process_remove_command(target_pattern="no-such-target.pdf")
            output: str = mock_out.getvalue()
            self.assertTrue(
                "ERROR: cannot access /A/no-such-target.pdf" in output,
                msg=f"Output was: {output}")