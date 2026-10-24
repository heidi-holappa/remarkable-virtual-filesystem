import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    NoSuchDirectoryError,
    NoSuchFileOrDirectoryError
)

from src.constant import (
    NO_SUCH_FILE_OR_DIRECTORY)


from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.cd import ChangeDirectoryCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_A, UUID_A0, UUID_B0, UUID_D_1)


class ChangeDirectoryCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.cd = ChangeDirectoryCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))


    # -------------------------------
    # cd instruction
    # -------------------------------
    def test_cd_without_args_sets_current_path_to_root(self) -> None:
        self.cd._repository.set_current_collection(UUID_A)
        self.cd.handle([])
        self.assertTrue(self.cd._repository.get_current_collection() == "")

    def test_cd_to_subpath_works(self) -> None:
        """
        Verifies that changing collection to a direct subcollection
        works. The intention is to verify that all paths in cd-method
        work as intended.

        Note: Change directory is tested more comprehensively in
        RemarkableWorkspace test suite
        """
        self.cd._repository.set_current_collection("")
        self.cd.handle(["A"])
        self.assertTrue(self.cd._repository.get_current_collection() == UUID_A)


    def test_cd_with_too_many_args(self) -> None:
        self.cd._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.cd.handle(["arg1", "arg2"])
            output: str = mock_out.getvalue()
            self.assertTrue("Usage: cd OR cd <path>" in output, msg=f"Output was: {output}")

    def test_cd_with_non_existing_path_informs_user_path_does_not_exist(self) -> None:
        self.cd._repository.set_current_collection("")
        path: str = "/path/does/not/exist"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.cd.handle([path])
            output: str = mock_out.getvalue()
            self.assertTrue(f"cd: {path}: No such file or directory" in output, msg=f"Output was: {output}")

    def test_cd_to_file_informs_user_the_targer_is_not_a_directory(self) -> None:
        self.cd._repository.set_current_collection("")
        path: str = "/A/Fairytale.pdf"
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.cd.handle([path])
            output: str = mock_out.getvalue()
            self.assertTrue(f"cd: {path}: Not a directory" in output, msg=f"Output was: {output}")

    def test_cd_to_collection_with_a_whitespace_in_its_visble_name(self) -> None:
        self.cd._repository.set_current_collection("")
        self.cd.handle(["D 1"])
        self.assertTrue(self.cd._repository.get_current_collection() == UUID_D_1)


    # -----------------------
    # Change collection/directory tests
    # -----------------------

    def test_change_collection_from_root_to_direct_subpath(self) -> None:
        self.cd.change_collection("/A")
        assert self.cd._repository.get_current_collection() == UUID_A

    def test_change_collection_from_root_to_direct_subpath_with_additional_slashes(self) -> None:
        self.cd.change_collection("//////////A")
        assert self.cd._repository.get_current_collection() == UUID_A

    def test_change_collection_from_root_to_direct_subpath_with_relative_directories(self) -> None:
        self.cd.change_collection("/././../A/..////A")
        assert self.cd._repository.get_current_collection() == UUID_A

    def test_change_collection_to_nested_subpath_with_absolute_path(self) -> None:
        self.cd.change_collection("/A/A_0")
        assert self.cd._repository.get_current_collection() == UUID_A0

    def test_change_collection_to_nested_subpath_with_relative_path(self) -> None:
        # assumming the collection is A before the path change
        self.cd.change_collection("/A")
        self.cd.change_collection("../B/B_0")
        # then the new path should be /B/B_0
        assert self.cd._repository.get_current_collection() == UUID_B0

    def test_change_collection_with_document_visible_name_raises_error(self) -> None:
        with self.assertRaises(NoSuchDirectoryError) as context:
            self.cd.change_collection("C")

        self.assertTrue("C: Not a directory" in str(context.exception))

    def test_change_collection_with_non_existing_path_raises_error(self) -> None:
        with self.assertRaises(NoSuchFileOrDirectoryError) as context:
            self.cd.change_collection("D")

        self.assertTrue(NO_SUCH_FILE_OR_DIRECTORY in str(context.exception))
