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

import unittest
import time
import uuid
from unittest.mock import patch, MagicMock
from io import BytesIO, StringIO
import tarfile
import json
from typing import Dict

from src.data.remarkable_ssh_metadata_source import RemarkableSSHMetadataSource


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
    def test_get_file_sizes_nonzero_returncode_raises(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = ("", "error")
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        with self.assertRaises(RuntimeError) as ctx:
            self.source._get_file_sizes()

        self.assertIn("error", str(ctx.exception))

    # --------------------------------------------------
    # is_valid_metadata()
    # (tests written by heidi-holappa)
    # --------------------------------------------------

    def test_valid_metadata_entry_is_accepted(self) -> None:
        valid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700239",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.assertTrue(self.source.is_valid_metadata(valid_metadata))

    def test_metadata_with_root_as_parent_is_accepted(self) -> None:
        valid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700239",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.assertTrue(self.source.is_valid_metadata(valid_metadata))

    def test_metadata_with_missing_key_parent_is_rejected(self) -> None:
        metadata_with_missing_parent_field: Dict[str, str | bool] = {
            "createdTime": "1768039700239",
            "lastModified": "1768039700238",
            "new": False,
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.assertFalse(self.source.is_valid_metadata(metadata_with_missing_parent_field))

    def test_metadata_with_additional_key_size_is_rejected(self) -> None:
        invalid_metadata_additional_key_size: Dict[str, str | bool] = {
            "createdTime": "1768039700239",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90",
            "size": "4 kB"
        }

        self.assertFalse(self.source.is_valid_metadata(invalid_metadata_additional_key_size))

    def test_metadata_with_invalid_created_time(self) -> None:
        expected_output = "invalid value in metadata field createdTime"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "-1",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)


    def test_case_invalid_value_in_field_last_modified(self) -> None:
        in_future_ms = int(time.time() * 1000) + 100000

        expected_output = "invalid value in metadata field lastModified"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": str(in_future_ms),
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_non_string_value_in_field_last_modified(self) -> None:
        expected_output = "invalid value in metadata field lastModified"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": 1768039700238,
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_edge_case_invalid_digit_value_in_field_last_modified(self) -> None:
        expected_output = "invalid value in metadata field lastModified"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "176803970023\u00B2",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_edge_case_too_small_value_in_field_last_modified(self) -> None:
        expected_output = "invalid value in metadata field lastModified"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "176803970023",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_invalid_value_in_field_new(self) -> None:
        expected_output = "invalid value in metadata field new"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": "false",
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)


    def test_case_invalid_string_value_in_field_parent(self) -> None:
        expected_output = "invalid value in metadata field parent"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": True,
            "parent": "123-456-xxy",
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_non_string_value_in_field_parent(self) -> None:
        expected_output = "invalid value in metadata field parent"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": True,
            "parent": uuid.uuid1,
            "pinned": False,
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)


    def test_case_invalid_value_in_field_pinned(self) -> None:
        expected_output = "invalid value in metadata field pinned"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": True,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": "true",
            "source": "",
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_invalid_value_in_field_source(self) -> None:
        expected_output = "invalid value in metadata field source"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": True,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": None,
            "type": "CollectionType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_invalid_value_in_field_type(self) -> None:
        expected_output = "invalid value in metadata field type"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "UnknownType",
            "visibleName": "61-90"
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def test_case_invalid_value_in_field_visible_name(self) -> None:
        expected_output = "invalid value in metadata field visibleName"
        invalid_metadata: Dict[str, str | bool] = {
            "createdTime": "1768039700238",
            "lastModified": "1768039700238",
            "new": False,
            "parent": "d433121d-b050-4740-8db7-0ed11b980371",
            "pinned": False,
            "source": "",
            "type": "DocumentType",
            "visibleName": None
        }

        self.invalid_value_in_given_field(invalid_metadata, expected_output)

    def invalid_value_in_given_field(self, invalid_metadata: Dict[str, str | bool],
                                          expected_output: str) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            validation_result: bool = self.source.is_valid_metadata(invalid_metadata)
            output: str = mock_out.getvalue()
            self.assertTrue(expected_output in output,
                            msg=f"Output did not match expected: {output}")
            self.assertFalse(validation_result)
