"""
    Module for stubbing reMarkable datasource
"""
from test.test_data_v2 import TEST_DATA
from typing import Dict
from src.dto.entry import Entry

from src.data.metadata_source_v2 import  MetadataSourceV2


class StubRemarkableMetadataSourceV2(MetadataSourceV2):
    """
    A class implementation of the stub
    """

    def load(self) -> Dict[str, Entry]:
        return TEST_DATA