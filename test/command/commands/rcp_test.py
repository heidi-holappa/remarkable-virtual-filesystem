import os
import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

from src.event.event_bus import EventBus
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2

from src.exception import NotFoundError, InvalidPathError

from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands import RemoteCopyCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2,
    UUID_B,
    UUID_FAIRYTALE_COPY,
    UUID_B0,
    UUID_A_UNDER_B, UUID_A0_UNDER_B,
    UUID_D_1,
    UUID_C)

class RemoteCopyCommandTest(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self.rcp = RemoteCopyCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()),
            EventBus())

    # -------------------------------
    # rcp instruction
    # -------------------------------
    def test_rcp_without_args(self) -> None:
        """
        When user attempts to use rcp instruction without
        arguments, they are instructed of the usage of
        the command
        """
        self.rcp._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rcp.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("rcp: usage:" in output, msg=f"Output was: {output}")

    def test_rcp_with_invalid_argument(self) -> None:
        """
        When user attempts to use rcp instruction with
        too many arguments, they are instructed of the
        usage of the command
        """
        self.rcp._repository.set_current_collection("")
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self.rcp.handle(["-x", "/path/to/foo.pdf", "bar/"])
            output: str = mock_out.getvalue()
            self.assertTrue("rcp: invalid options: -x" in output, msg=f"Output was: {output}")

    @patch.object(RemoteCopyCommand, "_process_rcp_command_without_options")
    def test_rcp_without_options_positive_case(self, mock_rcp: MagicMock) -> None:
        source = "path/to/file.txt"
        target = "./foo"
        self.rcp.handle([source, target])

        mock_rcp.assert_called_once()

        _, kwargs = mock_rcp.call_args
        self.assertEqual(kwargs['source_file'], source)
        self.assertEqual(kwargs['target_collection'], target)

    @patch.object(RemoteCopyCommand, "_process_rcp_with_options")
    def test_rcp_with_options_positive_case(self, mock_rcp: MagicMock) -> None:
        source = "path/to/"
        target = "./foo"
        flag = "-a"
        self.rcp.handle([flag, source, target])

        mock_rcp.assert_called_once()

        args_tuple, _ = mock_rcp.call_args
        list_of_args = args_tuple[0]
        self.assertEqual(list_of_args[0], flag)
        self.assertEqual(list_of_args[1], source)
        self.assertEqual(list_of_args[2], target)
        

    # -------------------------------------
    # Process remote copy command
    # -------------------------------------

    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
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

        self.rcp._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        source_file = "/path/to/file.pdf"
        target_path = "/"

        # ---- Execute ----
        self.rcp._process_rcp_command_without_options(source_file, target_path)

        # ---- Assertions ----

        # remote_copy called once
        mock_remote_copy.assert_called_once()


        # load called and assigned
        mock_load.assert_called_once()
        self.assertEqual(self.rcp._repository._in_memory_data, ["new_data"])

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

    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source_v2.os.walk")
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

        self.rcp._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        # ---- Execute ----
        self.rcp._process_rcp_with_options(["-a", source_path, target_path])

        # ---- Assertions ----

        # remote_copy called twice
        assert mock_remote_copy.call_count == 2

        # load called and assigned
        mock_load.assert_called_once()
        self.assertEqual(self.rcp._repository._in_memory_data, ["new_data"])

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

    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source_v2.os.walk")
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

        self.rcp._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        # ---- Execute ----
        self.rcp._process_rcp_with_options(["-r", source_path, target_path])

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

    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
    @patch("src.data.remarkable_ssh_metadata_source_v2.os.walk")
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

        self.rcp._traverse_path = MagicMock(return_value=UUID_ROOT) # type: ignore[method-assign]

        target_path = "/"

        with patch('sys.stdout', new=StringIO()) as mock_out:
            # ---- Execute ----
            self.rcp._process_rcp_with_options(["-r", source_path, target_path])
            output: str = mock_out.getvalue()
            self.assertTrue(
                "rcp: no pdf or epub files found in directory" in output,
                msg=f"Output was: {output}")


    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
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
        self.rcp._process_rcp_command_without_options(source_file, target_path)

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()

    @patch("builtins.print")
    @patch("src.data.remarkable_ssh_metadata_source_v2.os.path.exists")
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
        self.rcp._process_rcp_with_options(["-a", source_file, target_path])

        # ---- Assertions ----

        # Nothing should be called
        mock_remote_copy.assert_not_called()
        mock_restart.assert_not_called()
        mock_load.assert_not_called()

        # Error was printed
        mock_print.assert_called_once()


    def test_process_rcp_with_invalid_args(self) -> None:
        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.rcp._process_rcp_with_options(["-q", "/some/path/to/file.pdf", "/"])
            output: str = mock_out.getvalue()
            self.assertTrue("rcp: invalid options: -q" in output, msg=output)


    @patch.object(RemarkableSSHMetadataSourceV2, "remote_copy")
    def test_copy_file_from_host_to_target_when_remote_copy_fails(
            self, mock_remote_copy: MagicMock) -> None:
        mock_remote_copy.side_effect = NotFoundError("file not found")

        source_file = "/tmp/foo.pdf"
        target_uuid = str(UUID_A)

        with patch("sys.stdout", new=StringIO()) as mock_out:
            self.rcp._copy_file_from_host_to_target(source_file, target_uuid)

            self.assertEqual(mock_remote_copy.call_count, 1)
            output: str = mock_out.getvalue()
            self.assertIn("file not found", output)


    # -------------------
    # _get_or_create_collection
    # -------------------
    def test_when_child_already_exists_it_is_returned(self) -> None:
        parent_uuid = UUID_A
        child_visible_name = "A_0"
        actual_uuid = self.rcp._get_or_create_collection(parent_uuid, child_visible_name)
        self.assertEqual(UUID_A0, actual_uuid)

    # ----------------------------
    # _generate_target_path_uuid_and_source_file_pairs
    # ----------------------------
    def test_generate_target_path_uuid_and_source_file_pairs_skips_empty_directory(
            self) -> None:
        source_path = "/tmp/source"
        target_collection = str(UUID_A)
        files = ["/tmp/source//foo.pdf"]

        with patch.object(
                self.rcp,
                "_get_or_create_collection",
                return_value=str(UUID_B),
        ) as mock_get_or_create:
            result = self.rcp._generate_target_path_uuid_and_source_file_pairs(
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



    # --------------------------
    # Validate source and target uuid
    # --------------------------

    @patch("os.path.exists", return_value=True)
    def test_when_target_uuid_is_none_not_found_error_is_raised(
            self, mock_exists: MagicMock) -> None:
        with self.assertRaises(NotFoundError) as context:
            self.rcp._validate_source_and_target_uuid("", "/foo", None)

        mock_exists.assert_called_once_with("")

        self.assertTrue(
            "rcp: target path /foo not found" in str(context.exception),
            msg=context.exception
        )

    # -------------------------------------
    # Get descendants for CollectionType matching a pattern and all their children
    # -------------------------------------

    def test_descendants_for_collection_b_are_returned_correctly(self) -> None:

        actual_uuids = self.rcp._collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(
            "B*", UUID_ROOT
        )
        expected_uuids: list[str] = [UUID_B, UUID_FAIRYTALE_COPY, UUID_B0, UUID_A_UNDER_B, UUID_A0_UNDER_B]
        self.assertEqual(sorted(expected_uuids), sorted(actual_uuids))

    # -------------------------------------
    # Get descendants for CollectionType
    # -------------------------------------

    def test_descendants_are_returned_correctly_for_path_root(self) -> None:
        actual_descendants: list[str] = self.rcp._get_descendant_uuids(UUID_ROOT)
        expected_descendants: list[str] = [
            UUID_A, UUID_A0, UUID_A1,
            UUID_FAIRYTALE, UUID_FAIRYTALE_2,
            UUID_B,
            UUID_FAIRYTALE_COPY,
            UUID_B0,
            UUID_A_UNDER_B, UUID_A0_UNDER_B,
            UUID_D_1,
            UUID_C
        ]
        self.assertEqual(sorted(expected_descendants), sorted(actual_descendants))


    def test_descendants_are_returned_correctly_for_path_a(self) -> None:
        actual_descendants: list[str] = self.rcp._get_descendant_uuids(UUID_A)
        expected_descendants: list[str] = [
            UUID_A0, UUID_A1,
            UUID_FAIRYTALE, UUID_FAIRYTALE_2
        ]
        self.assertEqual(sorted(expected_descendants), sorted(actual_descendants))

    def test_when_no_descendants_exists_an_empty_list_is_returned(self) -> None:
        self.assertEqual([], self.rcp._get_descendant_uuids(UUID_A0))


    # -------------------------------------
    # Check if an entry with the given visibleName exists in the provided collection
    # -------------------------------------

    def test_returns_true_when_entry_exists(self) -> None:
        self.assertTrue(
            self.rcp._exists_visible_name_in_collection(UUID_FAIRYTALE, UUID_B)
        )

    def test_returns_false_when_entry_does_not_exist(self) -> None:
        self.assertFalse(
            self.rcp._exists_visible_name_in_collection(UUID_FAIRYTALE, UUID_B0)
        )

    def test_raise_not_found_exception_if_entry_does_not_exist(self) -> None:
        with self.assertRaises(NotFoundError) as ctx:
            self.assertFalse(
                self.rcp._exists_visible_name_in_collection("123-123", UUID_A)
            )

        self.assertTrue("Metadata not found for 123-123" in str(ctx.exception))


    # -------------------
    # _get_descendant_uuids
    # -------------------
    def test_when_when_entity_is_not_a_collection_error_is_raised(self) -> None:
        with self.assertRaises(InvalidPathError) as context:
            self.rcp._get_descendant_uuids(UUID_FAIRYTALE)

        self.assertTrue(f"Metadata for CollectionType not found: {UUID_FAIRYTALE}"
                        in str(context.exception), msg=context.exception)