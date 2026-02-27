import unittest
from io import StringIO
import copy
from unittest.mock import patch, MagicMock
from typing import List

from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource
from src.workspace.remarkable_workspace import RemarkableWorkspace
from src.exception.not_found_exception import NotFoundException
from src.exception.invalid_path_exception import InvalidPathException
from src.constant import COLLECTION_NOT_FOUND, INVALID_PATH
from test.test_data import (
    TEST_DATA,
    UUID_FAIRYTALE,
    UUID_A, UUID_A0,
    UUID_B, UUID_B0, UUID_ROOT, UUID_INVALID_LAST_MODIFIED)

class RemarkableWorkspaceTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSource, "load")
    def setUp(self, mock_load) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ws = RemarkableWorkspace(RemarkableSSHMetadataSource())

    # ----------------------
    # Get parent
    #-----------------------
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

    # -----------------------
    # Get collection
    # -----------------------
    def test_get_collection_when_current_collection_is_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A", "") == UUID_A

    def test_get_collection_when_current_collection_is_not_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A_0", UUID_A) == UUID_A0

    def test_get_collection_when_current_collection_is_root_and_collection_is_not_found(self) -> None:
        assert self.ws.get_collection("C", "") == None

    # -----------------------
    # Set current collection
    # -----------------------
    def test_set_current_collection_with_valid_collection(self) -> None:
        self.ws.set_current_collection(UUID_A)
        assert self.ws.get_current_collection() == UUID_A

    def test_set_current_collection_with_invalid_collection(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            self.ws.set_current_collection("c")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    # -----------------------
    # Change collection/directory tests
    # -----------------------
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

    # -----------------------
    # Get absolute path
    # -----------------------
    def test_root_path_is_output_correctly(self) -> None:
        self.assertEqual("/", self.ws.generate_absolute_collection_path(""))

    def test_direct_subdirectory_to_root_output_correctly(self) -> None:
        self.assertEqual("/A", self.ws.generate_absolute_collection_path(UUID_A))

    def test_nested_subdirectory_output_correctly(self) -> None:
        self.assertEqual("/A/A_0", self.ws.generate_absolute_collection_path(UUID_A0))

    # -----------------------
    # Get current path
    # -----------------------
    def test_root_path_is_returned_correctly(self) -> None:
        self.ws.set_current_collection('')
        self.assertEqual('/', self.ws.get_current_path())

    def test_path_is_returned_correctly(self) -> None:
        self.ws.set_current_collection(UUID_A)
        self.assertEqual('/A', self.ws.get_current_path())

    # -----------------------
    # Handle move instruction
    # -----------------------
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_without_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.handle_move_instruction("Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_absolute_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.handle_move_instruction("/A/Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_relative_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A0)
        self.ws.handle_move_instruction("../Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    # Constraint: Source must be a valid file or collection (case: moving DocumentType)
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_invalid_source_filename_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/C/non-existing-file.pdf", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("Metadata not found for" in output, msg=f"Output was: {output}")

    # Constraint: Source must be a valid file or collection (case: moving CollectionType)
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_invalid_source_path_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/C", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("Metadata not found for" in output, msg=f"Output was: {output}")

    # Constraint: destination must resolve to valid collection
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_with_invalid_target_path_error_is_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A/Fairytale.pdf", "/C")
            output: str = mock_out.getvalue()
            self.assertTrue(INVALID_PATH in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_document_with_invalid_metadata_cannot_be_moved_and_error_is_shown(self, mock_write) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A/InvalidLastModified.pdf", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("One or more metadata fields have invalid values" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_relative_target_path(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A", "A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("Collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_absolute_target_path(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A", "/A/A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("Collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_cannot_be_moved_into_itself(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A", "/A")
            output: str = mock_out.getvalue()
            self.assertTrue("Collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: Root collection can not be moved
    def test_root_collection_cannot_be_moved(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("", "")
            output: str = mock_out.getvalue()
            self.assertTrue("Root path cannot be moved" in output, msg=f"Output was: {output}")

    # Constraint: destination must not contain a child with the same name
    def test_destination_cannot_contain_child_with_the_same_visible_name(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.handle_move_instruction("/A", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("Destination must not contain a child with the same name" in output, msg=f"Output was: {output}")

    # Constraint: moving to the same parent should result in a no-op
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_moving_to_the_same_parent_should_result_in_no_op(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.handle_move_instruction("Fairytale.pdf", "/A")
        mock_write.assert_not_called()
        self.assertEqual(mock_write.call_count, 0)

    # -------------------------------------
    # Get wildcard matches
    # -------------------------------------

    def test_wild_card_match_finds_documents_with_pdf_extension(self) -> None:
        matches: List[str] = self.ws.get_matches_for_wildcard(UUID_A, "*.pdf")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)


    def test_wild_card_match_finds_document_matches_with_prefix(self) -> None:
        matches: List[str] = self.ws.get_matches_for_wildcard(UUID_A, "Fa*")
        self.assertEqual(1, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)

    def test_wild_card_match_finds_collection_matches_with_prefix(self) -> None:
        matches: List[str] = self.ws.get_matches_for_wildcard(UUID_A, "A_*")
        self.assertEqual(1, len(matches))
        self.assertTrue(UUID_A0 in matches)

    def test_wild_card_alone_matches_all_children(self) -> None:
        matches: List[str] = self.ws.get_matches_for_wildcard(UUID_A, "*")
        self.assertEqual(3, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)

    def test_wild_card_with_multiple_stars_finds_matches(self) -> None:
        matches: List[str] = self.ws.get_matches_for_wildcard(UUID_A, "*valid*.pdf")
        self.assertEqual(1, len(matches))
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)

    def test_raises_not_found_exception_if_parent_not_found(self) -> None:
        with self.assertRaises(NotFoundException) as ctx:
            self.ws.get_matches_for_wildcard("123-123", "*valid*.pdf")
        self.assertTrue(COLLECTION_NOT_FOUND in str(ctx.exception))

    # -------------------------------------
    # Check if an entry with the given visibleName exists in the provided collection
    # -------------------------------------

    def test_returns_true_when_entry_exists(self) -> None:
        self.assertTrue(
            self.ws.exists_entry_with_same_visible_name_in_target_path(UUID_FAIRYTALE, UUID_A)
        )

    def test_returns_false_when_entry_does_not_exist(self) -> None:
        self.assertFalse(
            self.ws.exists_entry_with_same_visible_name_in_target_path(UUID_FAIRYTALE, UUID_B)
        )

    def test_raise_not_found_exception_if_entry_does_not_exist(self) -> None:
        with self.assertRaises(NotFoundException) as ctx:
            self.assertFalse(
                self.ws.exists_entry_with_same_visible_name_in_target_path("123-123", UUID_A)
            )

        self.assertTrue("Metadata not found for 123-123" in str(ctx.exception))

    # -------------------------------------
    # Get UUID with visibleName and parent
    # -------------------------------------
    def test_when_file_is_found_uuid_is_returned(self) -> None:
        actual_file_uuid: str = self.ws.get_uuid_with_visible_name_and_parent(
            'Fairytale.pdf', UUID_A)
        self.assertEqual(UUID_FAIRYTALE, actual_file_uuid)

    def test_when_file_is_not_found_exception_is_raised(self) -> None:

        with self.assertRaises(NotFoundException) as context:
            self.ws.get_uuid_with_visible_name_and_parent(
                'Sadtale.pdf', UUID_B)

        self.assertTrue("Metadata not found for" in str(context.exception))

