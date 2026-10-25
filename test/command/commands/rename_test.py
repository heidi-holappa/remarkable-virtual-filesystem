import copy
from io import StringIO

from unittest.mock import patch, MagicMock
import unittest

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository

from test.test_data_v2 import (
    TEST_DATA,
    UUID_A,
    UUID_FAIRYTALE)


from src.command.commands import RenameCommand


class RenameCommandTest(unittest.TestCase):
    
    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.rename = RenameCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))


    # -------------------------------
    # method: handle
    # -------------------------------

    def test_rename_without_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.rename._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("rename: usage:" in output, msg=f"Output was: {output}")

    def test_rename_with_too_many_args(self) -> None:
        """
        When user attempts to use mv instruction with too
        many arguments, they are instructed of the usage of
        the command
        """
        self.rename._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.handle(["-r", "foo.pdf", "bar.pdf"])
            output: str = mock_out.getvalue()
            self.assertTrue("rename: usage:" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_positive_case(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.rename._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = "renamed-fairytale.pdf"
        self.rename.handle([target, new_visible_name])
        actual_visible_name = self.rename._repository.get_visible_name_for_uuid(UUID_FAIRYTALE)
        self.assertEqual(new_visible_name, actual_visible_name)
        self.assertEqual(1, mock_write.call_count)


    # -----------------------
    # method: process_rename
    # -----------------------


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_empty_string(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.rename._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = ""
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: visible name cannot be an empty string" in output,
                            msg=f"Output was: {output}")


    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_parent_already_has_child_with_same_name(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.rename._repository.set_current_collection(UUID_A)
        target = "Fairytale.pdf"
        new_visible_name = "Fairytale-2.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: parent has a child with the same name" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_invalid(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.rename._repository.set_current_collection(UUID_A)
        target = "A_0"
        new_visible_name = "A_00/"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}: visible name contains invalid characters" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableSSHMetadataSourceV2, "write_metadata")
    def test_rename_new_visible_name_target_not_found(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.rename._repository.set_current_collection(UUID_A)
        target = "Fairytale-not-found.pdf"
        new_visible_name = "renamed-fairytale.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rename.process_rename(target, new_visible_name)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(f"rename: {target} {new_visible_name}:" in output,
                            msg=f"Output was: {output}")
            self.assertTrue(
                "No such file or directory" in output,
                msg=f"Output was: {output}")
