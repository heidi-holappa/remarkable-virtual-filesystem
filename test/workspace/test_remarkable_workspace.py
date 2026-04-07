import unittest
import time
from io import StringIO
import copy
from unittest.mock import patch, MagicMock
from typing import List, Set

from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource
from src.dto.metadata import Metadata
from src.dto.content import Content
from src.dto.file_type_enum import FileType
from src.dto.entry_type_enum import EntityType
from src.exception.no_such_file_or_directory_exception import NoSuchFileOrDirectoryException
from src.exception.remarkable_operation_exception import RemarkableOperationException
from src.workspace.remarkable_workspace import RemarkableWorkspace
from src.exception.not_found_exception import NotFoundException
from src.constant import COLLECTION_NOT_FOUND, INVALID_PATH, PARENT_NOT_FOUND, NO_SUCH_FILE_OR_DIRECTORY
from test.test_data import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_B, UUID_B0, UUID_A_UNDER_B,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2,
    UUID_INVALID_LAST_MODIFIED, UUID_A0_UNDER_B, UUID_D_1)

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
        with self.assertRaises(NoSuchFileOrDirectoryException) as context:
            self.ws.change_collection("C")

        self.assertTrue(NO_SUCH_FILE_OR_DIRECTORY in str(context.exception))

    # -----------------------
    # Get absolute path
    # -----------------------
    def test_root_path_is_output_correctly(self) -> None:
        self.assertEqual("/", self.ws.generate_absolute_collection_path(UUID_ROOT))

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
        self.ws.process_move_command("Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_absolute_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.process_move_command("/A/Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_after_successful_move_with_relative_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A0)
        self.ws.process_move_command("../Fairytale.pdf", "/B")
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    # Constraint: Source must be a valid file or collection (case: moving DocumentType)
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_invalid_source_filename_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            source = "/C/non-existing-file.pdf"
            self.ws.process_move_command(source, "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}" in output,
                            msg=f"Output was: {output}")

    # Constraint: Source must be a valid file or collection (case: moving CollectionType)
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_invalid_source_path_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/C", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: cannot access /C: {NO_SUCH_FILE_OR_DIRECTORY} " in output, msg=f"Output was: {output}")

    # Constraint: destination must resolve to valid collection
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_with_invalid_target_path_error_is_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A/Fairytale.pdf", "/C")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: /C: {NO_SUCH_FILE_OR_DIRECTORY}" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_document_with_invalid_metadata_cannot_be_moved_and_error_is_shown(self, mock_write) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A/InvalidLastModified.pdf", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("one or more metadata fields have invalid values" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_relative_target_path(self) -> None:
        self.ws.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_absolute_target_path(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/A/A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_cannot_be_moved_into_itself(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/A")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: Root collection can not be moved
    def test_root_collection_cannot_be_moved(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("", "")
            output: str = mock_out.getvalue()
            self.assertTrue("mv: root path cannot be moved" in output, msg=f"Output was: {output}")

    # Constraint: destination must not contain a child with the same name
    def test_destination_cannot_contain_child_with_the_same_visible_name(self) -> None:
        self.ws.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name" in output, msg=f"Output was: {output}")

    # Constraint: moving to the same parent should result in a no-op
    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_moving_to_the_same_parent_should_result_in_no_op(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.process_move_command("Fairytale.pdf", "/A")
        mock_write.assert_not_called()
        self.assertEqual(mock_write.call_count, 0)

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_single_document(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.process_move_command("*le.pdf", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_single_document_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_ROOT)
        self.ws.process_move_command("/A/*le.pdf", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_single_document_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_B)
        self.ws.process_move_command("../A/*le.pdf", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_single_collection_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_ROOT)
        self.ws.process_move_command("/A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_A1]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_single_collection_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_B)
        self.ws.process_move_command("../A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_A1]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_multiple_valid_documents(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.ws.process_move_command("Fairytale*.pdf", "/B")
        self.assertEqual(mock_write.call_count, 2)
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])
        self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE_2]['parent'])

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_one_collection_exists_in_destination_one_collection_moved(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.set_current_collection(UUID_B)
            self.ws.process_move_command("A*", "/A")
            self.assertEqual(mock_write.call_count, 1)
            self.assertEqual(UUID_A, self.ws.get_data()[UUID_A_UNDER_B]['parent'])
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name: A_0" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_one_document_has_invalid_metadata(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.set_current_collection(UUID_A)
            self.ws.process_move_command("*.pdf", "/B")
            self.assertEqual(mock_write.call_count, 2)
            self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])
            self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE_2]['parent'])
            output: str = mock_out.getvalue()
            self.assertTrue("mv: one or more metadata fields have invalid values: lastModified: -1" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_both_collections_and_documents_one_document_has_invalid_metadata_and_collection_with_same_name_exists_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.set_current_collection(UUID_A)
            self.ws.process_move_command("*", "/B")
            self.assertEqual(mock_write.call_count, 3)
            self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE]['parent'])
            self.assertEqual(UUID_B, self.ws.get_data()[UUID_FAIRYTALE_2]['parent'])
            self.assertEqual(UUID_B, self.ws.get_data()[UUID_A1]['parent'])
            output: str = mock_out.getvalue()
            self.assertTrue("mv: one or more metadata fields have invalid values: lastModified: -1" in output,
                            msg=f"Output was: {output}")
            self.assertTrue("mv: destination must not contain a child with the same name: A_0" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSource, "write")
    def test_move_with_wild_card_three_matching_collections_but_one_has_filename_already_present_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws.set_current_collection(UUID_B)
        self.ws.process_move_command("*", "/A")
        self.assertEqual(mock_write.call_count, 2)
        self.assertEqual(UUID_A, self.ws.get_data()[UUID_B0]['parent'])
        self.assertEqual(UUID_A, self.ws.get_data()[UUID_A_UNDER_B]['parent'])

    # -------------------------------------
    # Process remove instruction
    # -------------------------------------

    @patch.object(RemarkableSSHMetadataSource, "remove")
    def test_remove_one_document_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.ws.get_data())
        self.ws.process_remove_command(target_pattern="Fairytale.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.ws.get_data().get(UUID_FAIRYTALE))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = [UUID_FAIRYTALE]
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSource, "remove")
    def test_remove_two_documents_with_wildcard_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.ws.get_data())
        self.assertIn(UUID_FAIRYTALE_2, self.ws.get_data())
        self.ws.process_remove_command(target_pattern="Fairytale*.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.ws.get_data().get(UUID_FAIRYTALE))
        self.assertIsNone(self.ws.get_data().get(UUID_FAIRYTALE_2))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = sorted([UUID_FAIRYTALE, UUID_FAIRYTALE_2])
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSource, "remove")
    def test_remove_collection_recursively(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws.set_current_collection(UUID_ROOT)

        expected_removals: Set[str] = {
            UUID_A, UUID_A0, UUID_A1,
            UUID_FAIRYTALE,
            UUID_FAIRYTALE_2,
            UUID_INVALID_LAST_MODIFIED
        }
        self.assertTrue(expected_removals.issubset(self.ws.get_data()))

        self.ws.process_remove_command(target_pattern="A")
        self.assertEqual(mock_remove.call_count, 1)

        args, kwargs = mock_remove.call_args
        passed_list = args[0]

        self.assertEqual(sorted(expected_removals), sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    # -------------------------------------
    # Process remote copy command
    # -------------------------------------

    from unittest.mock import patch, MagicMock

    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSource, "load")
    @patch.object(RemarkableSSHMetadataSource, "restart_xochitl")
    @patch.object(RemarkableSSHMetadataSource, "remote_copy")
    def test_process_rcp_success(
            self,
            mock_remote_copy: MagicMock,
            mock_restart: MagicMock,
            mock_load: MagicMock,
            mock_exists: MagicMock
    ) -> None:
        # ---- Setup mocks ----
        mock_exists.return_value = True
        mock_load.return_value = ["new_data"]

        self.ws._traverse_path = MagicMock(return_value=UUID_ROOT)

        source_file = "/path/to/file.pdf"
        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_command(source_file, target_path)

        # ---- Assertions ----

        # remote_copy called once
        mock_remote_copy.assert_called_once()

        # restart called
        mock_restart.assert_called_once()

        # load called and assigned
        mock_load.assert_called_once()
        self.assertEqual(self.ws._data, ["new_data"])

        # ---- Inspect arguments passed to remote_copy ----
        _, kwargs = mock_remote_copy.call_args

        self.assertEqual(kwargs["source_file"], source_file)

        metadata = kwargs["metadata"]
        content = kwargs["content"]

        # Verify metadata
        self.assertEqual(metadata.parent, UUID_ROOT)
        self.assertEqual(metadata.visible_name, "file.pdf")

        # Verify content
        self.assertEqual(content.file_type, "pdf")

    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSource, "load")
    @patch.object(RemarkableSSHMetadataSource, "restart_xochitl")
    @patch.object(RemarkableSSHMetadataSource, "remote_copy")
    def test_process_rcp_source_not_found(
            self,
            mock_remote_copy: MagicMock,
            mock_restart: MagicMock,
            mock_load: MagicMock,
            mock_exists: MagicMock,
            mock_print: MagicMock
    ) -> None:
        # ---- Setup ----
        mock_exists.return_value = False  # <-- triggers first branch

        source_file = "/does/not/exist.pdf"
        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_command(source_file, target_path)

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()

    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSource, "load")
    @patch.object(RemarkableSSHMetadataSource, "restart_xochitl")
    @patch.object(RemarkableSSHMetadataSource, "remote_copy")
    def test_process_rcp_source_not_found(
            self,
            mock_remote_copy: MagicMock,
            mock_restart: MagicMock,
            mock_load: MagicMock,
            mock_exists: MagicMock,
            mock_print: MagicMock
    ) -> None:
        # ---- Setup ----
        mock_exists.return_value = False  # <-- triggers first branch

        source_file = "/does/not/exist.pdf"
        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_command(source_file, target_path)

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()

    # -------------------------------------
    # Process refresh command
    # -------------------------------------
    @patch.object(RemarkableSSHMetadataSource, "restart_xochitl")
    def test_refresh_invokes_metadata_source(self, mock_restart) -> None:

        self.ws.restart_xochitl()
        mock_restart.assert_called_once()

    @patch.object(RemarkableSSHMetadataSource, "restart_xochitl")
    def test_refresh_raises_exception_when_refresh_fails(self, mock_restart) -> None:
        mock_restart.side_effect = RemarkableOperationException("failure")

        with self.assertRaises(RemarkableOperationException) as context:
            self.ws.restart_xochitl()
        
        mock_restart.assert_called_once()

    # -------------------------------------
    # Get wildcard matches
    # -------------------------------------

    def test_wild_card_match_finds_documents_with_pdf_extension(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "*.pdf")
        self.assertEqual(3, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)


    def test_wild_card_match_finds_document_matches_with_prefix(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "Fa*")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)

    def test_wild_card_match_finds_collection_matches_with_prefix(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "A_*")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_A1 in matches)

    def test_wild_card_alone_matches_all_children(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "*")
        self.assertEqual(5, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_A1 in matches)
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)

    def test_wild_card_with_multiple_stars_finds_matches(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "*valid*.pdf")
        self.assertEqual(1, len(matches))
        self.assertTrue(UUID_INVALID_LAST_MODIFIED in matches)

    def test_raises_not_found_exception_if_parent_not_found(self) -> None:
        parent: str = "123-123"
        entity_wildcard = "*valid*.pdf"
        with self.assertRaises(NotFoundException) as ctx:
            self.ws._get_matches_for_wildcard(parent, entity_wildcard)
        self.assertTrue(PARENT_NOT_FOUND.format(
            parent=parent, entity=entity_wildcard) in str(ctx.exception), msg=ctx.exception)


    # -------------------------------------
    # Check if an entry with the given visibleName exists in the provided collection
    # -------------------------------------

    def test_returns_true_when_entry_exists(self) -> None:
        self.assertTrue(
            self.ws._exists_entry_with_same_visible_name_in_target_path(UUID_FAIRYTALE, UUID_A)
        )

    def test_returns_false_when_entry_does_not_exist(self) -> None:
        self.assertFalse(
            self.ws._exists_entry_with_same_visible_name_in_target_path(UUID_FAIRYTALE, UUID_B)
        )

    def test_raise_not_found_exception_if_entry_does_not_exist(self) -> None:
        with self.assertRaises(NotFoundException) as ctx:
            self.assertFalse(
                self.ws._exists_entry_with_same_visible_name_in_target_path("123-123", UUID_A)
            )

        self.assertTrue("Metadata not found for 123-123" in str(ctx.exception))

    # -------------------------------------
    # Get UUID with visibleName and parent
    # -------------------------------------
    def test_when_file_is_found_uuid_is_returned(self) -> None:
        actual_file_uuid: str = self.ws._get_uuid_with_visible_name_and_parent(
            'Fairytale.pdf', UUID_A)
        self.assertEqual(UUID_FAIRYTALE, actual_file_uuid)

    def test_when_file_is_not_found_exception_is_raised(self) -> None:

        with self.assertRaises(NotFoundException) as context:
            self.ws._get_uuid_with_visible_name_and_parent(
                'Sadtale.pdf', UUID_B)

        self.assertTrue(f"cannot access /B/Sadtale.pdf: {NO_SUCH_FILE_OR_DIRECTORY}" in str(context.exception),
                        msg=context.exception)


    # -------------------------------------
    # Get descendants for CollectionType
    # -------------------------------------

    def test_descendants_are_returned_correctly_for_path_root(self) -> None:
        actual_descendants: List[str] = self.ws._get_descendant_uuids(UUID_ROOT)
        expected_descendants: List[str] = [
            UUID_A, UUID_A0, UUID_A1,
            UUID_FAIRYTALE, UUID_FAIRYTALE_2,
            UUID_INVALID_LAST_MODIFIED,
            UUID_B, UUID_B0,
            UUID_A_UNDER_B, UUID_A0_UNDER_B,
            UUID_D_1
        ]
        self.assertEqual(sorted(expected_descendants), sorted(actual_descendants))


    def test_descendants_are_returned_correctly_for_path_a(self) -> None:
        actual_descendants: List[str] = self.ws._get_descendant_uuids(UUID_A)
        expected_descendants: List[str] = [
            UUID_A0, UUID_A1,
            UUID_FAIRYTALE, UUID_FAIRYTALE_2,
            UUID_INVALID_LAST_MODIFIED
        ]
        self.assertEqual(sorted(expected_descendants), sorted(actual_descendants))

    def test_when_no_descendants_exists_an_empty_list_is_returned(self) -> None:
        self.assertEqual([], self.ws._get_descendant_uuids(UUID_A0))

    # -------------------------------------
    # Get descendants for CollectionType matching a pattern and all their children
    # -------------------------------------

    def test_descendants_for_collection_b_are_returned_correctly(self) -> None:

        actual_uuids = self.ws._collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(
            "B*", UUID_ROOT
        )
        expected_uuids: List[str] = [UUID_B, UUID_B0, UUID_A_UNDER_B, UUID_A0_UNDER_B]
        self.assertEqual(sorted(expected_uuids), sorted(actual_uuids))
