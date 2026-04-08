import unittest
import time

from src.data.metadata_source import MetadataSource
from src.dto.content import Content
from src.dto.entry_type_enum import EntityType
from src.dto.file_type_enum import FileType
from src.dto.metadata import Metadata
from test.test_data import TEST_DATA, UUID_FAIRYTALE

class TestMetadataSource(unittest.TestCase):


    def setUp(self):
        self.source = MetadataSource()


    def test_load_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.load()


    def test_refresh_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.refresh()


    def test_write_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.write_metadata(
                UUID_FAIRYTALE,
                Metadata.from_dict(TEST_DATA.get(UUID_FAIRYTALE)))

    def test_remove_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.remove([UUID_FAIRYTALE])

    def test_remote_copy_raises_not_implemented_error(self) -> None:
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

        with self.assertRaises(NotImplementedError) as ctx:
            self.source.remote_copy("/path/to/file.txt", metadata, content)


    def test_restart_xochitl_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.restart_xochitl()