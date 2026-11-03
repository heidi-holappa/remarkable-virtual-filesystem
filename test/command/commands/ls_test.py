import copy
import unittest
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (NotFoundError)
from src.event.event import OutputMessage, OutputCommandMessage

from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.ls import ListCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0,
    UUID_B)


class ListCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.ls = ListCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())

    # -------------------------------
    # handle method call
    # -------------------------------
    def test_ls_root(self) -> None:
        self.ls._repository.set_current_collection("")
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])
            mock_publish.assert_any_call(OutputMessage("4               A/"))
            mock_publish.assert_any_call(OutputMessage("4               B/"))

    def test_ls_sub_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])
            mock_publish.assert_any_call(OutputMessage("4               A_0/"))

    def test_ls_file_with_size(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])
            mock_publish.assert_any_call(OutputMessage("1024            Fairytale.pdf"))


    def test_ls_with_too_many_args_informs_of_usage(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle(["a", "b"])
            mock_publish.assert_called_once_with(
                OutputCommandMessage(
                    "ls",
                    "usage: ls or ls <path or file>"
                )
            )

    def test_ls_with_valid_absolute_path_as_arg_lists_files_in_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle(["A"])
            mock_publish.assert_any_call(OutputMessage("1024            Fairytale.pdf"))

    def test_ls_with_valid_relative_path_as_arg_lists_files_in_path(self) -> None:
        self.ls._repository.set_current_collection(UUID_B)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle(["../A"])
            mock_publish.assert_any_call(OutputMessage("1024            Fairytale.pdf"))

    def test_ls_with_invalid_path_informs_user_path_not_found(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle(["path-does-not-exist"])
            mock_publish.assert_called_once_with(
                OutputCommandMessage(
                    "ls",
                    "no such path"
                )
            )

    def test_ls_full_output_for_root(self) -> None:
        self.ls._repository.set_current_collection(UUID_ROOT)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])
            mock_publish.assert_any_call(OutputMessage("size (kB)       name"))
            mock_publish.assert_any_call(OutputMessage("                ./"))
            mock_publish.assert_any_call(OutputMessage("4               A/"))
            mock_publish.assert_any_call(OutputMessage("4               B/"))
            mock_publish.assert_any_call(OutputMessage("4               D 1/"))

    def test_ls_full_output_for_dir_with_files(self) -> None:
        self.ls._repository.set_current_collection(UUID_A)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])


            mock_publish.assert_any_call(OutputMessage("size (kB)       name"))
            mock_publish.assert_any_call(OutputMessage("                ../"))
            mock_publish.assert_any_call(OutputMessage("                ./"))
            mock_publish.assert_any_call(OutputMessage("4               A_0/"))
            mock_publish.assert_any_call(OutputMessage("4               A_1/"))
            mock_publish.assert_any_call(OutputMessage("4096            Fairytale-2.pdf"))
            mock_publish.assert_any_call(OutputMessage("1024            Fairytale.pdf"))

    def test_ls_full_output_for_dir_without_files_or_subdirectories(self) -> None:
        self.ls._repository.set_current_collection(UUID_A0)
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            self.ls.handle([])
            mock_publish.assert_any_call(OutputMessage("size (kB)       name"))
            mock_publish.assert_any_call(OutputMessage("                ../"))
            mock_publish.assert_any_call(OutputMessage("                ./"))

    # -----------------------
    # process ls command method call
    # -----------------------

    def test_ls_raises_when_collection_not_found(self) -> None:
        with patch.object(self.ls._event_bus, "publish") as mock_publish:
            with self.assertRaises(NotFoundError) as ctx:
                self.ls._process_ls(["/not-found/"])

            self.assertTrue("no such path" in str(ctx.exception))

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
