import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (NotFoundError)

from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.ls import ListCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_B,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2)


class ListCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ls = ListCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    # -------------------------------
    # handle method call
    # -------------------------------
    def test_ls_root(self) -> None:
        self.ls._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("A/" in output, msg=f"Output was: {output}")
            self.assertTrue("B/" in output, msg=f"Output was: {output}")

    def test_ls_sub_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("A_0/" in output, msg=f"Output was: {output}")

    def test_ls_file_with_size(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_too_many_args_informs_of_usage(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle(["a", "b"])
            output: str = mock_out.getvalue()
            self.assertTrue("ls: usage: ls" in output, msg=f"Output was: {output}")

    def test_ls_with_valid_absolute_path_as_arg_lists_files_in_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle(["A"])
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_valid_relative_path_as_arg_lists_files_in_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_B)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle(["../A"])
            output: str = mock_out.getvalue()
            self.assertTrue("1024" in output, msg=f"Output was: {output}")
            self.assertTrue("Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_with_invalid_path_informs_user_path_not_found(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle(["path-does-not-exist"])
            output: str = mock_out.getvalue()
            self.assertTrue("ls: no such path" in output, msg=f"Output was: {output}")

    def test_ls_full_output_for_root(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("size (kB)       name" in output, msg=f"Output was: {output}")
            self.assertTrue("                ./" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               B/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               D 1/" in output, msg=f"Output was: {output}")

    def test_ls_full_output_for_dir_with_files(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("size (kB)       name" in output, msg=f"Output was: {output}")
            self.assertTrue("                ../" in output, msg=f"Output was: {output}")
            self.assertTrue("                ./" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A_0/" in output, msg=f"Output was: {output}")
            self.assertTrue("4               A_1/" in output, msg=f"Output was: {output}")
            self.assertTrue("4096            Fairytale-2.pdf" in output, msg=f"Output was: {output}")
            self.assertTrue("1024            Fairytale.pdf" in output, msg=f"Output was: {output}")

    def test_ls_full_output_for_dir_without_files_or_subdirectories(self) -> None:
        self.ls._repository.set_current_collection(UUID_A0)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.handle([])
            output: str = mock_out.getvalue()
            expected_output = """size (kB)       name
                ../
                ./
"""
            self.assertEqual(expected_output, output, msg=f"Output was: {output}")

    # -----------------------
    # process ls command method call
    # -----------------------

    def test_ls_happy_path_returns_correct_listing(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.ls.process_ls(args=[])
            output: str = mock_out.getvalue()

            in_memory_data = self.ls._repository.get_data()

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

    def test_ls_raises_when_collection_not_found(self) -> None:
        with self.assertRaises(NotFoundError) as ctx:
            self.ls.process_ls(["/not-found/"])

        self.assertTrue("ls: no such path" in str(ctx.exception))

    # -------------------
    # _traverse_path
    # -------------------
    def test_traverse_path_breaks_when_collection_pointer_is_not_string(self) -> None:
        # This should not happen, but we confirm this defensive check works
        with patch.object(
                self.ls._repository,
                "_current_collection",
                None,
        ):
            result = self.ls._traverse_path("foo")

        self.assertEqual(result, None)
