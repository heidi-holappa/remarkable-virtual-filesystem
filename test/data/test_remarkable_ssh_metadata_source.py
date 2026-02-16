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

These tests were initially generated with the assistance of a Large
Language Model (LLM) and subsequently reviewed and validated by a
human developer.

LLM used:
- Model: ChatGPT
- Version: GPT-5.2
- Provider: OpenAI
- Generation date: 2026-02-16
"""

import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import tarfile
import json

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
