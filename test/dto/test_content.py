"""
    Module for metadata DTO tests
"""

import unittest
import time

from src.dto.file_type_enum import FileType
from src.dto.content import Content
from src.exception.invalid_content_exception import InvalidContentException


class TestContent(unittest.TestCase):


    def test_valid_content_with_file_type_pdf_does_not_throw(self) -> None:
        content = Content(file_type=FileType.PDF)
        self.assertTrue("pdf", content.file_type.value)

    def test_valid_metadata_with_root_as_parent_does_not_throw(self) -> None:
        content = Content(file_type=FileType.EPUB)
        self.assertTrue("epub", content.file_type.value)

    def test_content_with_file_type_none_raises_exception(self) -> None:
        with self.assertRaises(InvalidContentException) as context:
            Content(file_type=None)

        self.assertTrue("fileType for content file must be an Enum FileType"
                        in str(context.exception), msg=context.exception)

    def test_content_with_file_type_str_raises_exception(self) -> None:
        with self.assertRaises(InvalidContentException) as context:
            Content(file_type="pdf")

        self.assertTrue("fileType for content file must be an Enum FileType"
                        in str(context.exception), msg=context.exception)