import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2

from src.exception import RemarkableWriteError

from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands import MakeDirectoryCommand 
from test.test_data_v2 import (
    TEST_DATA,
    UUID_A, UUID_B)

class MakeDirectoryCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.mkdir = MakeDirectoryCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    # -------------------------------
    # method: handle
    # -------------------------------
    def test_mkdir_with_multiple_args(self) -> None:
        """
        When user attempts to use mv instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.mkdir._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mkdir.handle(["-r", "foo.pdf", "bar/"])
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: usage: mkdir <path>" in output, msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_valid_directory_name(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mkdir._repository.set_current_collection(UUID_B)
        actual_path_to_make = "foo"
        self.mkdir.handle([actual_path_to_make])

        args, kwargs = mock_write.call_args
        actual_path_uuid = args[0]

        self.assertEqual(mock_write.call_count, 1)
        
        
    #--------------------------------------
    # Process mkdir (make directory)
    # --------------------------------------
    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_valid_directory_name_but_directory_exists(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mkdir._repository.set_current_collection(UUID_A)
        actual_path_to_make = "A_0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mkdir._process_mkdir(actual_path_to_make)
            self.assertEqual(mock_write.call_count, 0)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: A_0: path with same name already exists: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_invalid_directory_name(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mkdir._repository.set_current_collection(UUID_A)
        actual_path_to_make = "A#0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mkdir._process_mkdir(actual_path_to_make)
            self.assertEqual(mock_write.call_count, 0)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: A#0: path contains invalid characters: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_directory_name_with_path_fails(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mkdir._repository.set_current_collection(UUID_A)
        actual_path_to_make = "/A/A_0"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mkdir._process_mkdir(actual_path_to_make)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue("mkdir: /A/A_0: relative or absolute paths are not yet supported: hint: try help mkdir" in output,
                            msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_with_directory_name_empty_str(self, mock_write: MagicMock) -> None:
        mock_write.return_value = None
        self.mkdir._repository.set_current_collection(UUID_A)
        actual_path_to_make = ""
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.mkdir._process_mkdir(actual_path_to_make)
            self.assertEqual(0, mock_write.call_count)
            output: str = mock_out.getvalue()
            self.assertTrue(
                "mkdir: : path cannot be an empty string: hint: try help mkdir" in output,
                msg=f"Output was: {output}")

    @patch.object(RemarkableDataRepository, "write_metadata")
    def test_make_directory_when_write_metadata_fails(self, mock_write: MagicMock) -> None:
        mock_write.side_effect = RemarkableWriteError("write failed")
        self.mkdir._repository.set_current_collection(UUID_A)
        actual_path_to_make = "foo"

        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.mkdir._process_mkdir(actual_path_to_make)

            self.assertEqual(mock_write.call_count, 1)
            output: str = mock_out.getvalue()
            self.assertIn(
                "mkdir: foo: error writing to remarkable: write failed",
                output,
            )
