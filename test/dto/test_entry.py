import unittest
import uuid

from src.dto.content import Content
from src.dto.entry import Entry
from src.dto.metadata import Metadata
from src.dto.entry_type_enum import EntityType
from src.dto.file_type_enum import FileType


class TestEntry(unittest.TestCase):

    def test_can_create_entry(self) -> None:
        metadata = self.create_metadata()
        content = self.create_content()

        entry = Entry(
            metadata=metadata,
            content=content,
            size=1234,
        )

        self.assertIs(entry.metadata, metadata)
        self.assertIs(entry.content, content)
        self.assertEqual(entry.size, 1234)

    def test_entries_with_same_values_are_equal(self) -> None:
        metadata = self.create_metadata()
        content = self.create_content()

        entry1 = Entry(
            metadata=metadata,
            content=content,
            size=1234,
        )
        entry2 = Entry(
            metadata=metadata,
            content=content,
            size=1234,
        )

        self.assertEqual(entry1, entry2)

    def test_entries_with_different_sizes_are_not_equal(self) -> None:
        metadata = self.create_metadata()
        content = self.create_content()

        entry1 = Entry(
            metadata=metadata,
            content=content,
            size=1234,
        )
        entry2 = Entry(
            metadata=metadata,
            content=content,
            size=5678,
        )

        self.assertNotEqual(entry1, entry2)

    def test_entry_metadata_can_be_mutated(self) -> None:
        metadata = self.create_metadata()
        entry = Entry(
            metadata=metadata,
            content=self.create_content(),
            size=1234,
        )

        entry.metadata.visible_name = "renamed_doc.pdf"

        self.assertEqual(entry.metadata.visible_name, "renamed_doc.pdf")

    def test_entry_content_can_be_mutated(self) -> None:
        content = self.create_content()
        entry = Entry(
            metadata=self.create_metadata(),
            content=content,
            size=1234,
        )

        entry.content.file_type = FileType.EPUB

        self.assertEqual(entry.content.file_type, FileType.EPUB)

    def test_entry_metadata_can_be_replaced(self) -> None:
        metadata = self.create_metadata()
        entry = Entry(
            metadata=metadata,
            content=self.create_content(),
            size=1234,
        )

        new_metadata = self.create_metadata("new_doc.pdf")
        entry.metadata = new_metadata

        self.assertIs(entry.metadata, new_metadata)
        self.assertIsNot(entry.metadata, metadata)

    def test_entry_content_can_be_replaced(self) -> None:
        content = self.create_content()
        entry = Entry(
            metadata=self.create_metadata(),
            content=content,
            size=1234,
        )

        new_content = self.create_content(FileType.EPUB)
        entry.content = new_content

        self.assertIs(entry.content, new_content)
        self.assertIsNot(entry.content, content)

    def test_entry_size_can_be_mutated(self) -> None:
        entry = Entry(
            metadata=self.create_metadata(),
            content=self.create_content(),
            size=1234,
        )

        entry.size = 5678

        self.assertEqual(entry.size, 5678)


    def create_metadata(self, visible_name: str = "test_doc.pdf") -> Metadata:
        return Metadata(
            created_time=1700000000,
            last_modified=1700001000,
            new=False,
            parent=str(uuid.uuid4()),
            pinned=True,
            source="",
            type=EntityType.DOCUMENT_TYPE,
            visible_name=visible_name,
        )

    def create_content(self, file_type: FileType = FileType.PDF) -> Content:
        return Content(
            file_type=file_type,
        )


