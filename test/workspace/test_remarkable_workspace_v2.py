import copy
import os
import unittest
from io import StringIO
from typing import List, Set
from unittest.mock import patch, MagicMock

from src.constant import COLLECTION_NOT_FOUND, PARENT_NOT_FOUND, NO_SUCH_FILE_OR_DIRECTORY
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    RemarkableOperationError,
    NotFoundError,
    NoSuchFileOrDirectoryError,
    InvalidMetadataError,
    RemarkableWriteError,
    InvalidPathError
)
from src.workspace.remarkable_workspace_v2 import RemarkableWorkspaceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository
from test import test_data_v2
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_B, UUID_B0, UUID_A_UNDER_B,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2,
    UUID_A0_UNDER_B, UUID_D_1, UUID_FAIRYTALE_COPY)


class RemarkableWorkspaceV2Test(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ws = RemarkableWorkspaceV2(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    # -----------------------
    # process ls command
    # -----------------------

    def test_ls_happy_path_returns_correct_listing(self) -> None:
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_ls(utility_args=[])
            output: str = mock_out.getvalue()

            in_memory_data = self.ws._repository.get_data()

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

    # -----------------------
    # Handle move instruction
    # -----------------------
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_without_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.ws.process_move_command("Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.ws._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_with_absolute_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.ws.process_move_command("/A/Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.ws._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_with_relative_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A0)
        self.ws.process_move_command("../Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.ws._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    # Constraint: Source must be a valid file or collection (case: moving DocumentType)
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_invalid_source_filename_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            source = "/C/non-existing-file.pdf"
            self.ws.process_move_command(source, "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}" in output,
                            msg=f"Output was: {output}")


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_valid_wildcard_but_no_matches(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            source = "/A/no-such-prefix*"
            self.ws.process_move_command(source, "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}" in output,
                            msg=f"Output was: {output}")

    # Constraint: Source must be a valid file or collection (case: moving CollectionType)
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_invalid_source_path_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/C", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: cannot access /C: {NO_SUCH_FILE_OR_DIRECTORY} " in output, msg=f"Output was: {output}")


    # Constraint: destination must resolve to valid collection
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_with_invalid_target_path_error_is_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A/Fairytale.pdf", "/C")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: /C: {NO_SUCH_FILE_OR_DIRECTORY}" in output, msg=f"Output was: {output}")


    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_relative_target_path(self) -> None:
        self.ws._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_absolute_target_path(self) -> None:
        self.ws._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/A/A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_cannot_be_moved_into_itself(self) -> None:
        self.ws._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/A")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: Root collection can not be moved
    def test_root_collection_cannot_be_moved(self) -> None:
        self.ws._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("", "")
            output: str = mock_out.getvalue()
            self.assertTrue("mv: root path cannot be moved" in output, msg=f"Output was: {output}")

    # Constraint: destination must not contain a child with the same name
    def test_destination_cannot_contain_child_with_the_same_visible_name(self) -> None:
        self.ws._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("/A", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name" in output, msg=f"Output was: {output}")

    # Constraint: moving to the same parent should result in a no-op
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_moving_to_the_same_parent_should_result_in_no_op(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.ws.process_move_command("Fairytale.pdf", "/A")
        mock_write.assert_not_called()
        self.assertEqual(mock_write.call_count, 0)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.ws.process_move_command("*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.ws._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_ROOT)
        self.ws.process_move_command("/A/*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.ws._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_B)
        self.ws.process_move_command("../A/*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.ws._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_collection_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_ROOT)
        self.ws.process_move_command("/A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws._repository.get_data()[UUID_A1].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_collection_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_B)
        self.ws.process_move_command("../A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.ws._repository.get_data()[UUID_A1].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_multiple_valid_documents(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.ws.process_move_command("Fairytale*.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 2)
        self.assertEqual(UUID_B0, self.ws._repository.get_data()[UUID_FAIRYTALE].metadata.parent)
        self.assertEqual(UUID_B0, self.ws._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_one_collection_exists_in_destination_one_collection_moved(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws._repository.set_current_collection(UUID_B)
            self.ws.process_move_command("A*", "/A")
            self.assertEqual(mock_write.call_count, 1)
            self.assertEqual(UUID_A, self.ws._repository.get_data()[UUID_A_UNDER_B].metadata.parent)
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name: A_0" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_one_document_has_invalid_metadata(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws._repository.set_current_collection(UUID_A)
            self.ws.process_move_command("*.pdf", "/B/B_0")
            self.assertEqual(mock_write.call_count, 2)

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_move_with_wild_card_both_collections_and_documents_one_document_has_invalid_metadata_and_collection_with_same_name_exists_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws._repository.set_current_collection(UUID_A)
            self.ws.process_move_command("*", "/B")
            self.assertEqual(2, mock_write.call_count)

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_move_with_wild_card_three_matching_collections_but_one_has_filename_already_present_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_B)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_move_command("*", "/A")
            self.assertEqual(2, mock_write.call_count)

    # -----------------------
    # rename
    # -----------------------

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_positive_case(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = "renamed-fairytale.pdf"
        self.ws.process_rename(target, new_visible_name)
        actual_visible_name = self.ws._repository.get_visible_name_for_uuid(UUID_FAIRYTALE)
        self.assertEqual(new_visible_name, actual_visible_name)
        self.assertEqual(1, mock_write.call_count)


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_empty_string(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = ""
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: visible name cannot be an empty string" in output,
                            msg=f"Output was: {output}")


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_parent_already_has_child_with_same_name(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = "Fairytale-2.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: parent has a child with the same name" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_invalid(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        target = "A_0"
        new_visible_name = "A_00/"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: visible name contains invalid characters" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_target_not_found(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        target = "Fairytale-not-found.pdf"
        new_visible_name = "renamed-fairytale.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}:" in output,
                            msg=f"Output was: {output}")
            self.assertTrue(
                "No such file or directory" in output,
                msg=f"Output was: {output}")

    #--------------------------------------
    # Process mkdir (make directory)
    # --------------------------------------
    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_valid_directory_name(self,mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_B)
        actual_path_to_make = "foo"
        self.ws.process_mkdir(actual_path_to_make)

        args, kwargs = mock_write.call_args
        actual_path_uuid = args[0]

        self.assertEqual(mock_write.call_count, 1)

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_valid_directory_name_but_directory_exists(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        actual_path_to_make = "A_0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_mkdir(actual_path_to_make)
            self.assertEqual(mock_write.call_count, 0)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: A_0: path with same name already exists: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_invalid_directory_name(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        actual_path_to_make = "A#0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_mkdir(actual_path_to_make)
            self.assertEqual(mock_write.call_count, 0)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: A#0: path contains invalid characters: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_directory_name_with_path_fails(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        actual_path_to_make = "/A/A_0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_mkdir(actual_path_to_make)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: /A/A_0: relative or absolute paths are not yet supported: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_directory_name_empty_str(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        actual_path_to_make = ""
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_mkdir(actual_path_to_make)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(
                "mkdir: : path cannot be an empty string: hint: try help mkdir" in output,
                msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_when_write_metadata_fails(self, mock_write: MagicMock) -> None:
        mock_write.side_effect = RemarkableWriteError("write failed")
        self.ws._repository.set_current_collection(UUID_A)
        actual_path_to_make = "foo"

        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.ws.process_mkdir(actual_path_to_make)

            self.assertEqual(mock_write.call_count, 1)
            output: str = mock_out.getvalue()
            self.assertIn(
                "mkdir: foo: error writing to remarkable: write failed",
                output,
            )

    # -------------------------------------
    # Process remove instruction
    # -------------------------------------

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_one_document_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.ws._repository.get_data())
        self.ws.process_remove_command(target_pattern="Fairytale.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.ws._repository.get_data().get(UUID_FAIRYTALE))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = [UUID_FAIRYTALE]
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_two_documents_with_wildcard_positive_case(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws._repository.set_current_collection(UUID_A)
        self.assertIn(UUID_FAIRYTALE, self.ws._repository.get_data())
        self.assertIn(UUID_FAIRYTALE_2, self.ws._repository.get_data())
        self.ws.process_remove_command(target_pattern="Fairytale*.pdf")
        self.assertEqual(mock_remove.call_count, 1)
        self.assertIsNone(self.ws._repository.get_data().get(UUID_FAIRYTALE))
        self.assertIsNone(self.ws._repository.get_data().get(UUID_FAIRYTALE_2))

        args, kwargs = mock_remove.call_args
        passed_list = args[0]
        expected_uuids_to_remove = sorted([UUID_FAIRYTALE, UUID_FAIRYTALE_2])
        self.assertEqual(expected_uuids_to_remove, sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_collection_recursively(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws._repository.set_current_collection(UUID_ROOT)

        expected_removals: Set[str] = {
            UUID_A, UUID_A0, UUID_A1,
            UUID_FAIRYTALE,
            UUID_FAIRYTALE_2
        }
        self.assertTrue(expected_removals.issubset(self.ws._repository.get_data()))

        self.ws.process_remove_command(target_pattern="A")
        self.assertEqual(mock_remove.call_count, 1)

        args, kwargs = mock_remove.call_args
        passed_list = args[0]

        self.assertEqual(sorted(expected_removals), sorted(passed_list),
                         msg=f"Assertion failed. Passed list: {passed_list}")

    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_target_not_found(self, mock_remove: MagicMock) -> None:
        mock_remove.return_value = None
        self.ws._repository.set_current_collection(UUID_A)

        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ws.process_remove_command(target_pattern="no-such-target.pdf")
            output: str = mock_out.getvalue()
            self.assertTrue(
                "ERROR: cannot access /A/no-such-target.pdf" in output,
                msg=f"Output was: {output}")

    # -------------------------------------
    # Process remote copy command
    # -------------------------------------

    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_process_rcp_success_without_options(
            self,
            mock_remote_copy: MagicMock,
            mock_load: MagicMock,
            mock_exists: MagicMock
    ) -> None:
        # ---- Setup mocks ----
        mock_exists.return_value = True
        mock_load.return_value = ["new_data"]

        self.ws._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        source_file = "/path/to/file.pdf"
        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_command_without_options(source_file, target_path)

        # ---- Assertions ----

        # remote_copy called once
        mock_remote_copy.assert_called_once()


        # load called and assigned
        mock_load.assert_called_once()
        self.assertEqual(self.ws._repository._in_memory_data, ["new_data"])

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

    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source.os.walk")
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_process_rcp_success_with_valid_option_all(
            self,
            mock_remote_copy: MagicMock,
            mock_load: MagicMock,
            mock_walk: MagicMock,
            mock_exists: MagicMock,
    ) -> None:
        # ---- Setup mocks ----
        mock_exists.return_value = True
        source_path = os.getcwd()
        mock_walk.return_value = [(source_path, [], ["file1.pdf", "file2.epub"])]
        mock_load.return_value = ["new_data"]

        self.ws._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_with_options(["-a", source_path, target_path])

        # ---- Assertions ----

        # remote_copy called twice
        assert mock_remote_copy.call_count == 2

        # load called and assigned
        mock_load.assert_called_once()
        self.assertEqual(self.ws._repository._in_memory_data, ["new_data"])

        # ---- Inspect calls ----
        calls = mock_remote_copy.call_args_list

        expected = [
            ("file1.pdf", "pdf"),
            ("file2.epub", "epub"),
        ]

        for call, (filename, ext) in zip(calls, expected):
            kwargs = call.kwargs

            # source file
            self.assertIn(filename, kwargs["source_file"])

            # metadata
            metadata = kwargs["metadata"]
            self.assertEqual(metadata.parent, UUID_ROOT)
            self.assertEqual(metadata.visible_name, filename)

            # content
            content = kwargs["content"]
            self.assertEqual(content.file_type, ext)

    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source.os.walk")
    @patch.object(RemarkableDataRepository, "refresh_data")
    @patch.object(RemarkableDataRepository, "invoke_remote_copy")
    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_process_rcp_success_with_valid_option_recurse(
            self,
            mock_write_metadata: MagicMock,
            mock_remote_copy: MagicMock,
            mock_load: MagicMock,
            mock_walk: MagicMock,
            mock_exists: MagicMock
    ) -> None:
        # ---- Setup mocks ----
        mock_write_metadata.return_value = None
        mock_exists.return_value = True
        source_path = os.getcwd()
        mock_walk.return_value = [(source_path, [], ["file1.pdf", "path1/file2.epub"])]
        mock_load.return_value = ["new_data"]

        self.ws._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        # ---- Execute ----
        self.ws.process_rcp_with_options(["-r", source_path, target_path])

        # ---- Assertions ----

        # remote_copy called twice
        assert mock_remote_copy.call_count == 2


        # load called and assigned
        mock_load.assert_called_once()

        # ---- Inspect calls ----
        calls = mock_remote_copy.call_args_list

        # The boolean checks whether the parent is the root
        # ideally we would capture the uuid of each parent
        # but that is for future test expansions to add
        expected = [
            ("file1.pdf", "pdf", True),
            ("path1/file2.epub", "epub", False),
        ]

        for call, (filename, ext, has_root_as_parent) in zip(calls, expected):
            kwargs = call.kwargs

            # source file
            self.assertIn(filename, kwargs["source_file"])

            # metadata
            metadata = kwargs["metadata"]
            self.assertEqual(has_root_as_parent, metadata.parent == UUID_ROOT)

            # content
            content = kwargs["content"]
            self.assertEqual(content.file_type, ext)

    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source.os.walk")
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rcp_recursive_but_no_matches(
            self,
            mock_write_metadata: MagicMock,
            mock_load: MagicMock,
            mock_walk: MagicMock,
            mock_exists: MagicMock
    ) -> None:
        # ---- Setup mocks ----
        mock_write_metadata.return_value = None
        mock_exists.return_value = True
        source_path = os.getcwd()
        mock_walk.return_value = [(source_path, [], [])]
        mock_load.return_value = ["new_data"]

        self.ws._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        with patch('sys.stdout', new=StringIO()) as mock_out:
            # ---- Execute ----
            self.ws.process_rcp_with_options(["-r", source_path, target_path])
            output: str = mock_out.getvalue()
            self.assertTrue(
                "rcp: no pdf or epub files found in directory" in output,
                msg=f"Output was: {output}")


    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    @patch.object(RemarkableSSHMetadataSourceV2, "restart_xochitl")
    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_process_rcp_without_flags_source_not_found(
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
        self.ws.process_rcp_command_without_options(source_file, target_path)

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()

    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source.os.path.exists")
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    @patch.object(RemarkableSSHMetadataSourceV2, "restart_xochitl")
    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_process_rcp_with_valid_flags_source_not_found(
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
        self.ws.process_rcp_with_options(["-a", source_file, target_path])

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()

    # -------------------------------------
    # Get wildcard matches
    # -------------------------------------

    def test_wild_card_match_finds_documents_with_pdf_extension(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "*.pdf")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)


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
        self.assertEqual(4, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_A1 in matches)
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)

    def test_wild_card_with_multiple_stars_finds_matches(self) -> None:
        matches: List[str] = self.ws._get_matches_for_wildcard(UUID_A, "*le-2*.pdf")
        self.assertEqual(1, len(matches))

    def test_raises_not_found_exception_if_parent_is_not_a_parent(self) -> None:
        parent: str = UUID_FAIRYTALE
        entity_wildcard = "*valid*.pdf"
        with self.assertRaises(NotFoundError) as ctx:
            self.ws._get_matches_for_wildcard(parent, entity_wildcard)
        self.assertTrue(PARENT_NOT_FOUND.format(
            parent=parent, entity=entity_wildcard) in str(ctx.exception), msg=ctx.exception)

    def test_raises_not_found_exception_if_parent_uuid_does_not_exist(self) -> None:
        parent: str = "123-123"
        entity_wildcard = "*valid*.pdf"
        with self.assertRaises(NotFoundError) as ctx:
            self.ws._get_matches_for_wildcard(parent, entity_wildcard)
        self.assertTrue(PARENT_NOT_FOUND.format(
            parent=parent, entity=entity_wildcard) in str(ctx.exception), msg=ctx.exception)

    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_copy_file_from_host_to_target_when_remote_copy_fails(
            self, mock_remote_copy: MagicMock) -> None:
        mock_remote_copy.side_effect = NotFoundError("file not found")

        source_file = "/tmp/foo.pdf"
        target_uuid = str(UUID_A)

        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.ws._copy_file_from_host_to_target(source_file, target_uuid)

            self.assertEqual(mock_remote_copy.call_count, 1)
            output: str = mock_out.getvalue()
            self.assertIn("file not found", output)


    # -------------------------------------
    # Check if an entry with the given visibleName exists in the provided collection
    # -------------------------------------

    def test_returns_true_when_entry_exists(self) -> None:
        self.assertTrue(
            self.ws._exists_visible_name_in_collection(UUID_FAIRYTALE, UUID_B)
        )

    def test_returns_false_when_entry_does_not_exist(self) -> None:
        self.assertFalse(
            self.ws._exists_visible_name_in_collection(UUID_FAIRYTALE, UUID_B0)
        )

    def test_raise_not_found_exception_if_entry_does_not_exist(self) -> None:
        with self.assertRaises(NotFoundError) as ctx:
            self.assertFalse(
                self.ws._exists_visible_name_in_collection("123-123", UUID_A)
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

        with self.assertRaises(NotFoundError) as context:
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
            UUID_B,
            UUID_FAIRYTALE_COPY,
            UUID_B0,
            UUID_A_UNDER_B, UUID_A0_UNDER_B,
            UUID_D_1
        ]
        self.assertEqual(sorted(expected_descendants), sorted(actual_descendants))


    def test_descendants_are_returned_correctly_for_path_a(self) -> None:
        actual_descendants: List[str] = self.ws._get_descendant_uuids(UUID_A)
        expected_descendants: List[str] = [
            UUID_A0, UUID_A1,
            UUID_FAIRYTALE, UUID_FAIRYTALE_2
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
        expected_uuids: List[str] = [UUID_B, UUID_FAIRYTALE_COPY, UUID_B0, UUID_A_UNDER_B, UUID_A0_UNDER_B]
        self.assertEqual(sorted(expected_uuids), sorted(actual_uuids))



    # --------------------------
    # Validate source and target uuid
    # --------------------------

    @patch("os.path.exists", return_value=True)
    def test_when_target_uuid_is_none_not_found_error_is_raised(
            self, mock_exists: MagicMock) -> None:
        with self.assertRaises(NotFoundError) as context:
            self.ws._validate_source_and_target_uuid("", "/foo", None)

        mock_exists.assert_called_once_with("")

        self.assertTrue(
            "rcp: target path /foo not found" in str(context.exception),
            msg=context.exception
        )


    # ----------------------------
    # _generate_target_path_uuid_and_source_file_pairs
    # ----------------------------
    def test_generate_target_path_uuid_and_source_file_pairs_skips_empty_directory(
            self) -> None:
        source_path = "/tmp/source"
        target_collection = str(UUID_A)
        files = ["/tmp/source//foo.pdf"]

        with patch.object(
                self.ws,
                "_get_or_create_collection",
                return_value=str(UUID_B),
        ) as mock_get_or_create:
            result = self.ws._generate_target_path_uuid_and_source_file_pairs(
                source_path,
                files,
                target_collection,
            )

        # The empty directory component between the two '/' characters
        # should have been skipped.
        mock_get_or_create.assert_not_called()
        self.assertEqual(
            result,
            [("/tmp/source//foo.pdf", target_collection)],
        )

    # -------------------
    # _get_or_create_collection
    # -------------------
    def test_when_child_already_exists_it_is_returned(self) -> None:
        parent_uuid = UUID_A
        child_visible_name = "A_0"
        actual_uuid = self.ws._get_or_create_collection(parent_uuid, child_visible_name)
        self.assertEqual(UUID_A0, actual_uuid)

    # -------------------
    # _get_descendant_uuids
    # -------------------
    def test_when_when_entity_is_not_a_collection_error_is_raised(self) -> None:
        with self.assertRaises(InvalidPathError) as context:
            self.ws._get_descendant_uuids(UUID_FAIRYTALE)

        self.assertTrue(f"Metadata for CollectionType not found: {UUID_FAIRYTALE}"
                        in str(context.exception), msg=context.exception)

    # -------------------
    # _traverse_path
    # -------------------
    def test_traverse_path_breaks_when_collection_pointer_is_not_string(self) -> None:
        # This should not happen, but we confirm this defensive check works
        with patch.object(
                self.ws._repository,
                "_current_collection",
                None,
        ):
            result = self.ws._traverse_path("foo")

        self.assertEqual(result, None)
