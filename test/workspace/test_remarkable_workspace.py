import unittest
import copy
from unittest.mock import patch

from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource
from src.workspace.remarkable_workspace import RemarkableWorkspace
from src.exception.not_found_exception import NotFoundException
from src.exception.invalid_path_exception import InvalidPathException
from src.constant import COLLECTION_NOT_FOUND, INVALID_PATH
from test.test_data import (
    TEST_DATA,
    UUID_FAIRYTALE,
    UUID_A, UUID_A0,
    UUID_B, UUID_B0)

class RemarkableWorkspaceTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSource, "load")
    def setUp(self, mock_load) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ws = RemarkableWorkspace(RemarkableSSHMetadataSource())

    # Get parent
    def test_get_parent_returns_correct_parent_when_parent_is_other_than_root(self) -> None:
        assert self.ws.get_parent(UUID_B0) == UUID_B

    def test_get_parent_return_correct_parent_when_parent_is_root(self) -> None:
        assert self.ws.get_parent(UUID_A) == ""

    def test_get_parent_handles_root_correctly(self) -> None:
        # per requirements root should return empty string
        assert self.ws.get_parent("") == ""

    def test_get_parent_for_collection_not_found_is_handled_gracefully(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            self.ws.get_parent("C")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    ## Get collection
    def test_get_collection_when_current_collection_is_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A", "") == UUID_A

    def test_get_collection_when_current_collection_is_not_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A_0", UUID_A) == UUID_A0

    def test_get_collection_when_current_collection_is_root_and_collection_is_not_found(self) -> None:
        assert self.ws.get_collection("C", "") == None

    # Set current collection
    def test_set_current_collection_with_valid_collection(self) -> None:
        self.ws.set_current_collection(UUID_A)
        assert self.ws.get_current_collection() == UUID_A

    def test_set_current_collection_with_invalid_collection(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            self.ws.set_current_collection("c")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    ## Change collection/directory tests
    def test_change_collection_from_root_to_direct_subpath(self) -> None:

        self.ws.change_collection("/A")
        assert self.ws.get_current_collection() == UUID_A

    def test_change_collection_from_root_to_direct_subpath_with_additional_slashes(self) -> None:
        self.ws.change_collection("//////////A")
        assert self.ws.get_current_collection() == UUID_A

    def test_change_collection_from_root_to_direct_subpath_with_relative_directories(self) -> None:
        self.ws.change_collection("/././../A/..////A")
        assert self.ws.get_current_collection() == UUID_A

    def test_change_collection_to_nested_subpath_with_absolute_path(self) -> None:
        self.ws.change_collection("/A/A_0")
        assert self.ws.get_current_collection() == UUID_A0

    def test_change_collection_to_nested_subpath_with_relative_path(self)  -> None:
        # assumming the collection is A before the path change
        self.ws.change_collection("/A")
        self.ws.change_collection("../B/B_0")
        # then the new path should be /B/B_0
        assert self.ws.get_current_collection() == UUID_B0

    def test_change_collection_with_invalid_path_raises_error(self) -> None:
        with self.assertRaises(InvalidPathException) as context:
            self.ws.change_collection("C")

        self.assertTrue(INVALID_PATH in str(context.exception))

    # Get absolute path
    def test_root_path_is_output_correctly(self) -> None:
        self.assertEqual("/", self.ws.generate_absolute_collection_path(""))

    def test_direct_subdirectory_to_root_output_correctly(self) -> None:
        self.assertEqual("/A", self.ws.generate_absolute_collection_path(UUID_A))

    def test_nested_subdirectory_output_correctly(self) -> None:
        self.assertEqual("/A/A_0", self.ws.generate_absolute_collection_path(UUID_A0))


    # Get current path
    def test_root_path_is_returned_correctly(self) -> None:
        self.ws.set_current_collection('')
        self.assertEqual('/', self.ws.get_current_path())

    def test_path_is_returned_correctly(self) -> None:
        self.ws.set_current_collection(UUID_A)
        self.assertEqual('/A', self.ws.get_current_path())


    # Handle move instruction
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_without_path_in_filename_parent_is_updated(self, mock_write) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.handle_move_instruction("Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    # Handle move instruction
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_absolute_path_in_filename_parent_is_updated(self, mock_write) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.handle_move_instruction("/A/Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    # Handle move instruction
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_relative_path_in_filename_parent_is_updated(self, mock_write) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A0)
        self.ws.handle_move_instruction("../Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    # Get UUID with visibleName and parent
    def test_when_file_is_found_uuid_is_returned(self) -> None:
        actual_file_uuid: str = self.ws.get_uuid_with_visible_name_and_parent(
            'Fairytale.pdf', UUID_A)
        self.assertEqual(UUID_FAIRYTALE, actual_file_uuid)

    # Get UUID with visibleName and parent
    def test_when_file_is_not_found_exception_is_raised(self) -> None:

        with self.assertRaises(NotFoundException) as context:
            self.ws.get_uuid_with_visible_name_and_parent(
                'Sadtale.pdf', UUID_B)

        self.assertTrue("Metadata not found for" in str(context.exception))

