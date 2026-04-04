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

    def test_do_dict_returns_valid_dictionary(self) -> None:
        content = Content(file_type=FileType.PDF)

        content_as_dict = content.to_dict()

        self.assertTrue(len(content_as_dict.keys()) == 1)
        self.assertEqual(FileType.PDF.value, content_as_dict.get("fileType"))


    def test_from_dict_creates_valid_content_instance(self) -> None:
        content_as_dict = {
            "fileType": "epub"
        }
        content = Content.from_dict(content_as_dict)
        self.assertEqual(FileType.EPUB.value, content.file_type.value)


    def test_from_dict_missing_field_raises_exception(self) -> None:
        with self.assertRaises(InvalidContentException) as context:
            Content.from_dict({})
        self.assertTrue("Missing content field" in str(context.exception))

    def test_from_dict_invalid_file_type(self) -> None:
        with self.assertRaises(InvalidContentException) as context:
            Content.from_dict({"fileType": "txt"})
        self.assertTrue("fileType: invalid value" in str(context.exception))

