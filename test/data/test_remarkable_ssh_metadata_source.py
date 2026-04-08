"""
Test suite for RemarkableSSHMetadataSource.

This module contains unit tests for the RemarkableSSHMetadataSource
class, including tests for:

- Successful metadata retrieval and parsing from tar archives
- Handling of SSH command failures
- Handling of missing metadata files
- Skipping invalid JSON metadata files
- File size aggregation parsing
- Error handling for size retrieval failures
- Proper merging of metadata and file size information

All interactions with the reMarkable device (SSH, subprocess calls,
and remote command execution) are fully mocked to ensure that tests
run deterministically and do not require a physical device.

The tests for _fetch_metadata and _get_files_sizes were initially
generated with the assistance of a Large Language Model (LLM) and
subsequently reviewed and validated by a human developer.

LLM used:
- Model: ChatGPT
- Version: GPT-5.2
- Provider: OpenAI
- Generation date: 2026-02-16
"""

import json
import subprocess
import tarfile
import time
import unittest
from io import BytesIO
from typing import Dict, List, Tuple
from unittest.mock import patch, MagicMock

from src.constant import SSH_CONNECT, REMOTE_PREFIX
from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource
from src.dto.content import Content
from src.dto.entry_type_enum import EntityType
from src.dto.file_type_enum import FileType
from src.dto.metadata import Metadata
from src.exception.remarkable_write_exception import RemarkableWriteException
from test.test_data import UUID_FAIRYTALE, UUID_FAIRYTALE_2

# System under test (SUT)
SUT: str = "src.data.remarkable_ssh_metadata_source"

class TestRemarkableSSHMetadataSource(unittest.TestCase):

    def setUp(self):
        self.source = RemarkableSSHMetadataSource()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _create_tar_bytes(self, files: dict[str, dict]) -> bytes:
        """
        Create an in-memory tar archive containing *.metadata files.
        `files` is a dict of uuid -> metadata_dict
        """
        tar_buffer = BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:") as tar:
            for uuid, metadata in files.items():
                file_data = json.dumps(metadata).encode("utf-8")
                tarinfo = tarfile.TarInfo(name=f"./{uuid}.metadata")
                tarinfo.size = len(file_data)
                tar.addfile(tarinfo, BytesIO(file_data))
        return tar_buffer.getvalue()

    # --------------------------------------------------
    # load()
    # --------------------------------------------------

    @patch.object(RemarkableSSHMetadataSource, "_get_file_sizes")
    @patch.object(RemarkableSSHMetadataSource, "_fetch_metadata")
    def test_load_merges_sizes(self, mock_fetch, mock_sizes):
        mock_fetch.return_value = {
            "uuid1": {"name": "doc1"},
            "uuid2": {"name": "doc2"},
        }
        mock_sizes.return_value = {
            "uuid1": 123,
            "uuid2": 456,
        }

        result = self.source.load()

        self.assertEqual(result["uuid1"]["size"], 123)
        self.assertEqual(result["uuid2"]["size"], 456)

    # --------------------------------------------------
    # _fetch_metadata()
    # --------------------------------------------------

    @patch("subprocess.Popen")
    @patch.object(RemarkableSSHMetadataSource, "_get_file_sizes")
    def test_fetch_metadata_success(self, mock_sizes, mock_popen):
        tar_bytes = self._create_tar_bytes({
            "uuid1": {"name": "doc1"},
            "uuid2": {"name": "doc2"},
        })

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (tar_bytes, b"")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        mock_sizes.return_value = {"uuid1": 100}

        result = self.source._fetch_metadata()

        self.assertIn("uuid1", result)
        self.assertEqual(result["uuid1"]["name"], "doc1")
        self.assertEqual(result["uuid1"]["size"], 100)

        self.assertIn("uuid2", result)
        self.assertEqual(result["uuid2"]["name"], "doc2")
        self.assertNotIn("size", result["uuid2"])

    @patch("subprocess.Popen")
    def test_fetch_metadata_nonzero_returncode_raises(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"", b"error")
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        with self.assertRaises(RuntimeError) as ctx:
            self.source._fetch_metadata()

        self.assertIn("error", str(ctx.exception))

    @patch("subprocess.Popen")
    def test_fetch_metadata_no_tar_bytes_raises(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"", b"")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        with self.assertRaises(RuntimeError) as ctx:
            self.source._fetch_metadata()

        self.assertIn("No metadata files found", str(ctx.exception))

    @patch("subprocess.Popen")
    @patch.object(RemarkableSSHMetadataSource, "_get_file_sizes")
    def test_fetch_metadata_invalid_json_skipped(self, mock_sizes, mock_popen):
        # Create tar with one invalid JSON file
        tar_buffer = BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:") as tar:
            bad_data = b"{invalid json"
            tarinfo = tarfile.TarInfo(name="./uuid1.metadata")
            tarinfo.size = len(bad_data)
            tar.addfile(tarinfo, BytesIO(bad_data))
        tar_bytes = tar_buffer.getvalue()

        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (tar_bytes, b"")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        mock_sizes.return_value = {}

        result = self.source._fetch_metadata()

        self.assertEqual(result, {})

    # --------------------------------------------------
    # _get_file_sizes()
    # --------------------------------------------------

    @patch("subprocess.Popen")
    def test_get_file_sizes_success(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (
            "uuid1\t100\nuuid2\t200\n",
            ""
        )
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        result = self.source._get_file_sizes()

        self.assertEqual(result["uuid1"], 100)
        self.assertEqual(result["uuid2"], 200)

    @patch("subprocess.Popen")
    def test_get_file_sizes_nonzero_return_code_raises(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "error")
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        with self.assertRaises(RuntimeError) as ctx:
            self.source._get_file_sizes()

        self.assertIn("error", str(ctx.exception))

    # --------------------------------------------------
    # write_metadata_to_remarkable()
    # --------------------------------------------------

    @patch("subprocess.Popen")
    def test_metadata_write_operation_succeeds(self, mock_popen) -> None:
        # And assuming the process finished successfully
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0

        mock_popen.return_value.__enter__.return_value = mock_proc

        # When method under test is invoked
        entry_uuid, valid_metadata_as_dict = self.call_write_metadata_to_remarkable_with_valid_data()


        # Then the remote device is called with the correct instruction
        expected_filename = f"{entry_uuid}.metadata"
        expected_cmd = REMOTE_PREFIX + f"cat > '{expected_filename}'"

        mock_popen.assert_called_once_with(
            SSH_CONNECT + [expected_cmd],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Then communicate is passed the correct JSON data as an argument
        expected_content = json.dumps(valid_metadata_as_dict, indent=4)
        mock_proc.communicate.assert_called_once_with(expected_content)

    @patch("subprocess.Popen")
    def test_metadata_write_fails_with_returncode(self, mock_popen) -> None:
        # And assuming the process finished successfully
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 1

        mock_popen.return_value.__enter__.return_value = mock_proc


        with self.assertRaises(RemarkableWriteException) as context:
            self.call_write_metadata_to_remarkable_with_valid_data()


        self.assertTrue("Failed to write metadata" in str(context.exception))

    @patch("subprocess.Popen", side_effect=OSError('test'))
    def test_metadata_write_fails_due_to_os_error(self, mock_popen) -> None:
        with self.assertRaises(RemarkableWriteException) as context:
            self.call_write_metadata_to_remarkable_with_valid_data()

        self.assertTrue("OS error while writing metadata" in str(context.exception))


    def call_write_metadata_to_remarkable_with_valid_data(self) -> Tuple[str, Dict[str, str | bool]]:
        # Assuming the method under test is provided a valid UUID
        entry_uuid = "327edac1-e3ca-4e1d-a4e0-e042603407c8"

        # Assuming the method under test is provided valid metadata
        valid_metadata = Metadata(
            created_time=1768039700239,
            last_modified=1768039700238,
            new=False,
            parent="d433121d-b050-4740-8db7-0ed11b980371",
            pinned=False,
            source="",
            type=EntityType.COLLECTION_TYPE,
            visible_name="61-90"
        )

        self.source.write_metadata(entry_uuid, valid_metadata)

        return entry_uuid, valid_metadata.to_dict()

    # --------------------------------------------------
    # remove()
    # --------------------------------------------------

    @patch("subprocess.Popen")
    def test_remove_positive_case(self, mock_popen) -> None:
        # Assuming popen process finished successfully
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 0

        mock_popen.return_value.__enter__.return_value = mock_proc

        uuids: List[str] = [UUID_FAIRYTALE, UUID_FAIRYTALE_2]

        # When method under test is invoked
        self.source.remove(uuids)

        # Then the remote device is called with the correct instruction
        expected_cmd = REMOTE_PREFIX + f"rm -rf -- {UUID_FAIRYTALE}* {UUID_FAIRYTALE_2}*"

        mock_popen.assert_called_once_with(
            SSH_CONNECT + [expected_cmd],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    @patch("subprocess.Popen", side_effect=OSError('test'))
    def test_remove_fails_due_to_os_error(self, mock_popen) -> None:
        with self.assertRaises(RemarkableWriteException) as context:
            self.source.remove([UUID_FAIRYTALE])

        self.assertTrue("OS error while removing files:" in str(context.exception))

    @patch("subprocess.Popen")
    def test_remove_fails_due_process_error_code(self, mock_popen) -> None:
        # And assuming the process finished successfully
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "")
        mock_proc.returncode = 1

        mock_popen.return_value.__enter__.return_value = mock_proc

        with self.assertRaises(RemarkableWriteException) as context:
            self.source.remove([UUID_FAIRYTALE])

        self.assertTrue("Failed to remove files:" in str(context.exception))

    # --------------------------------------------------
    # remote copy
    # --------------------------------------------------

    @patch(f"{SUT}.subprocess.Popen")
    def test_remote_copy_success(self, mock_popen) -> None:
        # ---- Mock processes ----
        mock_tar_proc = MagicMock()
        mock_ssh_proc = MagicMock()

        # tar stdout must exist (pipe to ssh)
        mock_tar_proc.stdout = MagicMock()

        # ssh behavior
        mock_ssh_proc.communicate.return_value = (None, None)
        mock_ssh_proc.returncode = 0

        # Popen is called twice: return tar, then ssh
        mock_popen.side_effect = [mock_tar_proc, mock_ssh_proc]


        source_file: str = "e2e-test/test/document-0.pdf"


        metadata: Metadata = Metadata(
            created_time=int(time.time()),
            last_modified=int(time.time()),
            new=False,
            parent="",
            pinned=False,
            source="",
            type=EntityType.DOCUMENT_TYPE,
            visible_name="file.pdf"
        )

        content: Content = Content(file_type=FileType.PDF)

        with patch(f"{SUT}.shutil.copy"), \
                patch(f"{SUT}.open", create=True), \
                patch(f"{SUT}.json.dump"):

            self.source.remote_copy(source_file=source_file, metadata=metadata, content=content)

        # ---- Assertions ----
        self.assertEqual(mock_popen.call_count, 2)

        mock_ssh_proc.communicate.assert_called_once()
        mock_tar_proc.stdout.close.assert_called_once()

        calls = mock_popen.call_args_list

        tar_cmd = calls[0][0][0]
        ssh_cmd = calls[1][0][0]

        self.assertEqual(tar_cmd[0], "tar")
        self.assertEqual(ssh_cmd[0], "ssh")

        _, ssh_kwargs = mock_popen.call_args_list[1]
        self.assertEqual(ssh_kwargs["stdin"], mock_tar_proc.stdout)

    @patch(f"{SUT}.subprocess.Popen")
    def test_remote_copy_ssh_failure(self, mock_popen) -> None:
        # ---- Mock processes ----
        mock_tar_proc = MagicMock()
        mock_ssh_proc = MagicMock()

        mock_tar_proc.stdout = MagicMock()

        # Simulate failure
        mock_ssh_proc.communicate.return_value = (None, None)
        mock_ssh_proc.returncode = 1  # <-- key change

        mock_popen.side_effect = [mock_tar_proc, mock_ssh_proc]

        source_file = "e2e-test/test/document-0.pdf"

        metadata = Metadata(
            created_time=int(time.time()),
            last_modified=int(time.time()),
            new=False,
            parent="",
            pinned=False,
            source="",
            type=EntityType.DOCUMENT_TYPE,
            visible_name="file.pdf"
        )

        content = Content(file_type=FileType.PDF)

        with patch(f"{SUT}.shutil.copy"), \
                patch(f"{SUT}.open", create=True), \
                patch(f"{SUT}.json.dump"):
            with self.assertRaises(RemarkableWriteException):
                self.source.remote_copy(
                    source_file=source_file,
                    metadata=metadata,
                    content=content
                )

        # ---- Assertions  ----
        self.assertEqual(mock_popen.call_count, 2)
        mock_ssh_proc.communicate.assert_called_once()
        mock_tar_proc.stdout.close.assert_called_once()

        # Verify piping still happened before failure
        _, ssh_kwargs = mock_popen.call_args_list[1]
        self.assertEqual(ssh_kwargs["stdin"], mock_tar_proc.stdout)

    from unittest.mock import patch

    # --------------------------------------------------
    # restart xochitl
    # --------------------------------------------------

    @patch("src.data.remarkable_ssh_metadata_source.subprocess.run")
    def test_restart_xochitl_success(self, mock_run) -> None:
        # ---- Mock subprocess result ----
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        mock_run.return_value = mock_result

        # ---- Call method ----
        RemarkableSSHMetadataSource.restart_xochitl()

        # ---- Assertions ----
        mock_run.assert_called_once()

        args, kwargs = mock_run.call_args

        # Verify command
        assert args[0][0] == "ssh"
        assert "systemctl restart xochitl" in args[0]

        # Verify subprocess options
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True