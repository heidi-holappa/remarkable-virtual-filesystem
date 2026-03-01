import unittest

from src.data.metadata_source import MetadataSource
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
            self.source.write(
                UUID_FAIRYTALE,
                Metadata.from_dict(TEST_DATA.get(UUID_FAIRYTALE)))

    def test_remove_raises_not_implemented_error(self) -> None:
        with self.assertRaises(NotImplementedError) as ctx:
            self.source.remove(UUID_FAIRYTALE)