"""
    Module for stubbing reMarkable datasource
"""
from test.test_data import TEST_DATA
from typing import Any, Dict

from src.data.metadata_source import  MetadataSource


class StubRemarkableMetadataSource(MetadataSource):
    """
    A class implementation of the stub
    """

    def load(self) -> Dict[str, Any]:
        return TEST_DATA