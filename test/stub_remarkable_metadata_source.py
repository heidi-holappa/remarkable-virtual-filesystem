"""
    Module for stubbing reMarkable datasource
"""
from test.test_data import TEST_DATA

from src.data.metadata_source import  MetadataSource


class StubRemarkableMetadataSource(MetadataSource):
    """
    A class implementation of the stub
    """

    def load(self):
        return TEST_DATA