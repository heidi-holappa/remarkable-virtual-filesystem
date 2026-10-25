import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2

from src.exception import NotFoundError, InvalidPathError

from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.mv import MoveCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_A, UUID_A0, UUID_A1,
    UUID_B, UUID_B0, UUID_A_UNDER_B,
    UUID_ROOT,
    UUID_FAIRYTALE_2, UUID_FAIRYTALE)

from src.constant import NO_SUCH_FILE_OR_DIRECTORY, PARENT_NOT_FOUND

class MoveCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.mv = MoveCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    # -------------------------------
    # handle method
    # -------------------------------
    def test_mv_without_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.mv._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("Usage (mvp):" in output, msg=f"Output was: {output}")

    def test_mv_with_too_many_args(self) -> None:
        """
        When user attempts to use mv instruction with too
        many arguments, they are instructed of the usage of
        the command
        """
        self.mv._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.handle(["-r", "foo.pdf", "bar/"])
            output: str = mock_out.getvalue()
            self.assertTrue("Usage (mvp):" in output, msg=f"Output was: {output}")

    @patch.object(MoveCommand, "process_move_command")
    def test_mv_positive_case(self, mock_move: MagicMock) -> None:
        source = "file.txt"
        target = "./foo"
        self.mv.handle([source, target])

        mock_move.assert_called_once()

        _, kwargs = mock_move.call_args
        self.assertEqual(kwargs['operand_source'], source)
        self.assertEqual(kwargs['operand_target'], target)


    # -----------------------
    # method: process move command 
    # -----------------------
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_without_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        self.mv.process_move_command("Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.mv._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_with_absolute_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        self.mv.process_move_command("/A/Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.mv._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_after_successful_move_with_relative_path_in_filename_parent_is_updated(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A0)
        self.mv.process_move_command("../Fairytale-2.pdf", "/B")
        self.assertEqual(UUID_B, self.mv._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    # Constraint: Source must be a valid file or collection (case: moving DocumentType)
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_invalid_source_filename_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            source = "/E/non-existing-file.pdf"
            self.mv.process_move_command(source, "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}" in output,
                            msg=f"Output was: {output}")


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_valid_wildcard_but_no_matches(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            source = "/A/no-such-prefix*"
            self.mv.process_move_command(source, "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}" in output,
                            msg=f"Output was: {output}")

    # Constraint: Source must be a valid file or collection (case: moving CollectionType)
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_invalid_source_path_results_in_error_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/E", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: cannot access /E: {NO_SUCH_FILE_OR_DIRECTORY} " in output, msg=f"Output was: {output}")


    # Constraint: destination must resolve to valid collection
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_with_invalid_target_path_error_is_shown_to_user(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/A/Fairytale.pdf", "/E")
            output: str = mock_out.getvalue()
            self.assertTrue(f"mv: /E: {NO_SUCH_FILE_OR_DIRECTORY}" in output, msg=f"Output was: {output}")


    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_relative_target_path(self) -> None:
        self.mv._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/A", "A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_type_cannot_be_moved_to_its_descendant_with_absolute_target_path(self) -> None:
        self.mv._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/A", "/A/A_0")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: A collection can not be moved into itself or its descendant
    def test_collection_cannot_be_moved_into_itself(self) -> None:
        self.mv._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/A", "/A")
            output: str = mock_out.getvalue()
            self.assertTrue("collection can not be moved into itself or its descendant" in output, msg=f"Output was: {output}")

    # Constraint: Root collection can not be moved
    def test_root_collection_cannot_be_moved(self) -> None:
        self.mv._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("", "")
            output: str = mock_out.getvalue()
            self.assertTrue("mv: root path cannot be moved" in output, msg=f"Output was: {output}")

    # Constraint: destination must not contain a child with the same name
    def test_destination_cannot_contain_child_with_the_same_visible_name(self) -> None:
        self.mv._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("/A", "/B")
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name" in output, msg=f"Output was: {output}")

    # Constraint: moving to the same parent should result in a no-op
    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_moving_to_the_same_parent_should_result_in_no_op(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        self.mv.process_move_command("Fairytale.pdf", "/A")
        mock_write.assert_not_called()
        self.assertEqual(mock_write.call_count, 0)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        self.mv.process_move_command("*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.mv._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_ROOT)
        self.mv.process_move_command("/A/*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.mv._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_document_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_B)
        self.mv.process_move_command("../A/*le.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B0, self.mv._repository.get_data()[UUID_FAIRYTALE].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_collection_absolute_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_ROOT)
        self.mv.process_move_command("/A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.mv._repository.get_data()[UUID_A1].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_single_collection_relative_path(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_B)
        self.mv.process_move_command("../A/A_1", "/B")
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(UUID_B, self.mv._repository.get_data()[UUID_A1].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_multiple_valid_documents(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_A)
        self.mv.process_move_command("Fairytale*.pdf", "/B/B_0")
        self.assertEqual(mock_write.call_count, 2)
        self.assertEqual(UUID_B0, self.mv._repository.get_data()[UUID_FAIRYTALE].metadata.parent)
        self.assertEqual(UUID_B0, self.mv._repository.get_data()[UUID_FAIRYTALE_2].metadata.parent)

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_one_collection_exists_in_destination_one_collection_moved(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv._repository.set_current_collection(UUID_B)
            self.mv.process_move_command("A*", "/A")
            self.assertEqual(mock_write.call_count, 1)
            self.assertEqual(UUID_A, self.mv._repository.get_data()[UUID_A_UNDER_B].metadata.parent)
            output: str = mock_out.getvalue()
            self.assertTrue("destination must not contain a child with the same name: A_0" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_move_with_wild_card_one_document_has_invalid_metadata(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv._repository.set_current_collection(UUID_A)
            self.mv.process_move_command("*.pdf", "/B/B_0")
            self.assertEqual(mock_write.call_count, 2)

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_move_with_wild_card_both_collections_and_documents_one_document_has_invalid_metadata_and_collection_with_same_name_exists_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv._repository.set_current_collection(UUID_A)
            self.mv.process_move_command("*", "/B")
            self.assertEqual(2, mock_write.call_count)

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_move_with_wild_card_three_matching_collections_but_one_has_filename_already_present_in_destination(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mv._repository.set_current_collection(UUID_B)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mv.process_move_command("*", "/A")
            self.assertEqual(2, mock_write.call_count)


    # -------------------------------------
    # Get wildcard matches
    # -------------------------------------

    def test_wild_card_match_finds_documents_with_pdf_extension(self) -> None:
        matches: list[str] = self.mv._get_matches_for_wildcard(UUID_A, "*.pdf")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)


    def test_wild_card_match_finds_document_matches_with_prefix(self) -> None:
        matches: list[str] = self.mv._get_matches_for_wildcard(UUID_A, "Fa*")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)

    def test_wild_card_match_finds_collection_matches_with_prefix(self) -> None:
        matches: list[str] = self.mv._get_matches_for_wildcard(UUID_A, "A_*")
        self.assertEqual(2, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_A1 in matches)

    def test_wild_card_alone_matches_all_children(self) -> None:
        matches: list[str] = self.mv._get_matches_for_wildcard(UUID_A, "*")
        self.assertEqual(4, len(matches))
        self.assertTrue(UUID_A0 in matches)
        self.assertTrue(UUID_A1 in matches)
        self.assertTrue(UUID_FAIRYTALE in matches)
        self.assertTrue(UUID_FAIRYTALE_2 in matches)

    def test_wild_card_with_multiple_stars_finds_matches(self) -> None:
        matches: list[str] = self.mv._get_matches_for_wildcard(UUID_A, "*le-2*.pdf")
        self.assertEqual(1, len(matches))

    def test_raises_not_found_exception_if_parent_is_not_a_parent(self) -> None:
        parent: str = UUID_FAIRYTALE
        entity_wildcard = "*valid*.pdf"
        with self.assertRaises(NotFoundError) as ctx:
            self.mv._get_matches_for_wildcard(parent, entity_wildcard)
        self.assertTrue(PARENT_NOT_FOUND.format(
            parent=parent, entity=entity_wildcard) in str(ctx.exception), msg=ctx.exception)

    def test_raises_not_found_exception_if_parent_uuid_does_not_exist(self) -> None:
        parent: str = "123-123"
        entity_wildcard = "*valid*.pdf"
        with self.assertRaises(NotFoundError) as ctx:
            self.mv._get_matches_for_wildcard(parent, entity_wildcard)
        self.assertTrue(PARENT_NOT_FOUND.format(
            parent=parent, entity=entity_wildcard) in str(ctx.exception), msg=ctx.exception)


    # -------------------------------------
    # Get UUID with visibleName and parent
    # -------------------------------------
    def test_when_file_is_found_uuid_is_returned(self) -> None:
        actual_file_uuid: str = self.mv._get_uuid_with_visible_name_and_parent(
            'Fairytale.pdf', UUID_A)
        self.assertEqual(UUID_FAIRYTALE, actual_file_uuid)

    def test_when_file_is_not_found_exception_is_raised(self) -> None:

        with self.assertRaises(NotFoundError) as context:
            self.mv._get_uuid_with_visible_name_and_parent(
                'Sadtale.pdf', UUID_B)

        self.assertTrue(f"cannot access /B/Sadtale.pdf: {NO_SUCH_FILE_OR_DIRECTORY}" in str(context.exception),
                        msg=context.exception)

