import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.constant import NOT_A_DIRECTORY
from src.dto.metadata import Metadata
from src.dto.entry import Entry
from src.constant import COLLECTION_NOT_FOUND
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    RemarkableOperationError,
    NotFoundError,
    NoSuchDirectoryError,
    RemarkableWriteError
)
from src.repository.remarkable_data_repository import RemarkableDataRepository
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0,
    UUID_B, UUID_B0)


class RemarkableWorkspaceTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.repository = RemarkableDataRepository(RemarkableSSHMetadataSourceV2())

    # ----------------------
    # Get parent
    # -----------------------
    def test_get_parent_returns_correct_parent_when_parent_is_other_than_root(self) -> None:
        assert self.repository.get_parent(UUID_B0) == UUID_B

    def test_get_parent_return_correct_parent_when_parent_is_root(self) -> None:
        assert self.repository.get_parent(UUID_A) == ""

    def test_get_parent_handles_root_correctly(self) -> None:
        # per requirements root should return empty string
        assert self.repository.get_parent("") == ""

    def test_get_parent_for_collection_not_found_is_handled_gracefully(self) -> None:
        with self.assertRaises(NotFoundError) as context:
            self.repository.get_parent("C")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    # -----------------------
    # Get collection
    # -----------------------
    def test_get_collection_when_current_collection_is_root_and_collection_is_found(self) -> None:
        assert self.repository.get_collection("A", UUID_ROOT) == UUID_A

    def test_get_collection_when_current_collection_is_not_root_and_collection_is_found(self) -> None:
        assert self.repository.get_collection("A_0", UUID_A) == UUID_A0

    def test_get_collection_when_parent_has_document_with_the_given_name_but_no_collectiion(self) -> None:
        with self.assertRaises(NoSuchDirectoryError) as ctx:
            self.repository.get_collection("C", UUID_ROOT)

        self.assertTrue(NOT_A_DIRECTORY in str(ctx.exception))

    def test_get_collection_when_current_collection_is_root_and_collection_is_not_found(self) -> None:
        self.assertIsNone(self.repository.get_collection("D", UUID_ROOT))

    # -----------------------
    # Set current collection
    # -----------------------
    def test_set_current_collection_with_valid_collection(self) -> None:
        self.repository.set_current_collection(UUID_A)
        assert self.repository.get_current_collection() == UUID_A

    def test_set_current_collection_with_invalid_collection(self) -> None:
        with self.assertRaises(NotFoundError) as context:
            self.repository.set_current_collection("c")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    # -----------------------
    # Get absolute path
    # -----------------------
    def test_root_path_is_output_correctly(self) -> None:
        self.assertEqual("/", self.repository.generate_absolute_collection_path(UUID_ROOT))

    def test_direct_subdirectory_to_root_output_correctly(self) -> None:
        self.assertEqual("/A", self.repository.generate_absolute_collection_path(UUID_A))

    def test_nested_subdirectory_output_correctly(self) -> None:
        self.assertEqual("/A/A_0", self.repository.generate_absolute_collection_path(UUID_A0))

    # -----------------------
    # Get current path
    # -----------------------
    def test_root_path_is_returned_correctly(self) -> None:
        self.repository.set_current_collection('')
        self.assertEqual('/', self.repository.get_current_path())

    def test_path_is_returned_correctly(self) -> None:
        self.repository.set_current_collection(UUID_A)
        self.assertEqual('/A', self.repository.get_current_path())

    # -------------------------------------
    # Get visible name for UUID
    # -------------------------------------

    def test_visible_name_for_root_is_empty_string(self) -> None:
        actual_root_visible_name = self.repository.get_visible_name_for_uuid('')
        self.assertTrue(actual_root_visible_name == '')

    def test_not_found_exception_is_thrown_for_non_existing_uuid(self) -> None:
        with self.assertRaises(NotFoundError) as context:
            self.repository.get_visible_name_for_uuid('some-uuid')
        self.assertTrue("Metadata not found for some-uuid" in str(context.exception),
                        msg=context.exception)

    # -------------------------------------
    # Get parent
    # -------------------------------------

    def test_returns_parent_of_current_collection_by_default(self) -> None:
        self.repository._current_collection = UUID_A0
        self.assertTrue(self.repository.get_parent() == UUID_A,
                        msg=f'get parent returned {self.repository.get_parent()}, '
                            f'which is NOT UUID of the parent of current collection (UUID_A): {UUID_A}')


    # -------------------------------------
    # Generate absolute collection path
    # -------------------------------------

    def test_when_collection_not_found_na_is_returned(self) -> None:
        invalid_data_uuid = "some-uuid"
        self.repository._in_memory_data.pop(invalid_data_uuid, None)
        actual_path = self.repository.generate_absolute_collection_path(invalid_data_uuid)
        self.assertEqual("./<NA>", actual_path)


    def test_when_parent_is_trash_child_is_trash_also(self) -> None:
        invalid_data_uuid = "some-uuid"
        self.repository._in_memory_data.pop(invalid_data_uuid, None)

        visible_name = "trash-document.pdf"

        metadata = {
            "type": "DocumentType",
            "parent": "trash",
            "visibleName": visible_name,
            "createdTime": 0,
            "lastModified": 123456789,
            "new": False,
            "pinned": False,
            "source": ""
        }

        invalid_data = Entry(
            metadata=Metadata.from_dict(metadata),
            size=1024,
            content=None
        )


        self.repository._in_memory_data[invalid_data_uuid] = invalid_data
        actual_path = self.repository.generate_absolute_collection_path(invalid_data_uuid)
        self.assertEqual(f"/trash/{visible_name}", actual_path)

    # -------------------------------------
    # Process refresh command
    # -------------------------------------
    def test_write_metadata_raises_when_uuid_not_found(self) -> None:
        metadata = {
            "type": "DocumentType",
            "parent": "trash",
            "visibleName": "some-document.pdf",
            "createdTime": 0,
            "lastModified": 123456789,
            "new": False,
            "pinned": False,
            "source": ""
        }

        with self.assertRaises(NotFoundError) as ctx:
            self.repository.write_metadata(
                "non-existing-uuid",
                Metadata.from_dict(metadata))

        self.assertTrue("No entry found for uuid" in str(ctx.exception))



    # -------------------
    # _remove_entities
    # -------------------
    @patch.object(RemarkableSSHMetadataSourceV2, "remove")
    def test_remove_entities_when_remove_fails(
            self, mock_remove: MagicMock) -> None:
        mock_remove.side_effect = RemarkableWriteError("write failed")

        entity_uuids = [str(UUID_A)]

        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.repository.remove_entities(entity_uuids)

        mock_remove.assert_called_once_with(entity_uuids)

        output: str = mock_out.getvalue()
        self.assertIn("ERROR: write failed", output)

    # -------------------
    # create_entry_if_absent
    # -------------------

    def test_create_entry_when_entry_is_absent(self) -> None:
        metadata_dict = {
            "type": "DocumentType",
            "parent": "trash",
            "visibleName": "some-document.pdf",
            "createdTime": 0,
            "lastModified": 123456789,
            "new": False,
            "pinned": False,
            "source": ""
        }

        metadata = Metadata.from_dict(metadata_dict)

        entry_uuid = "4eeab5d8-d7df-459a-a371-a8abdb3cfe17"

        entry: Entry = self.repository.create_entry_if_absent(
            entry_uuid,metadata)

        self.assertTrue(entry, msg=f"Entry does not exist: {entry_uuid}")
        if entry:
            self.assertEqual(metadata, entry.metadata,
                         msg=f"Metadata entries do not match. Expected: {metadata}, actual: {entry.metadata}")


    def test_create_if_absent_return_existing_entry(self) -> None:
        metadata_dict = {
            "type": "DocumentType",
            "parent": "trash",
            "visibleName": "some-document.pdf",
            "createdTime": 0,
            "lastModified": 123456789,
            "new": False,
            "pinned": False,
            "source": ""
        }

        metadata = Metadata.from_dict(metadata_dict)
        entry_uuid = UUID_A

        entry: Entry = self.repository.create_entry_if_absent(
            entry_uuid, metadata)

        self.assertTrue(entry, msg=f"Entry does not exist: {entry_uuid}")
        if entry:
            self.assertNotEqual(metadata, entry.metadata,
                         msg=f"Metadata entries match. Expected: {metadata}, actual: {entry.metadata}")

            entry_a = TEST_DATA.get(UUID_A)
            if entry_a:
                self.assertEqual(entry_a.metadata, entry.metadata,
                             msg=f"Metadata entries do not match. Expected: {metadata}, actual: {entry.metadata}")











    # -------------------
    # _remove_entry
    # -------------------
    def test_remove_raises_when_uuid_not_found(self) -> None:
        metadata = {
            "type": "DocumentType",
            "parent": "trash",
            "visibleName": "some-document.pdf",
            "createdTime": 0,
            "lastModified": 123456789,
            "new": False,
            "pinned": False,
            "source": ""
        }

        with self.assertRaises(NotFoundError) as ctx:
            self.repository.remove_entry("non-existing-uuid")

        self.assertTrue("No entry found for uuid" in str(ctx.exception))

    # -------------------------------------
    # Process refresh command
    # -------------------------------------
    @patch.object(RemarkableSSHMetadataSourceV2, "restart_xochitl")
    def test_refresh_invokes_metadata_source(self, mock_restart: MagicMock) -> None:
        self.repository.restart_xochitl()
        mock_restart.assert_called_once()

    @patch.object(RemarkableSSHMetadataSourceV2, "restart_xochitl")
    def test_refresh_raises_exception_when_refresh_fails(self, mock_restart: MagicMock) -> None:
        mock_restart.side_effect = RemarkableOperationError("failure")

        with self.assertRaises(RemarkableOperationError) as context:
            self.repository.restart_xochitl()

        mock_restart.assert_called_once()

