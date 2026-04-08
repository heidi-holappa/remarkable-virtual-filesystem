"""
    Module for metadata DTO tests
"""
import time
import unittest

from src.dto.entry_type_enum import EntityType
from src.dto.metadata import Metadata
from src.exception.invalid_metadata_exception import InvalidMetadataException


class TestMetadata(unittest.TestCase):


    def test_valid_metadata_does_not_throw(self) -> None:
        Metadata(
            created_time=int(time.time() * 1000),
            last_modified=int(time.time() * 1000),
            new=False,
            parent='d433121d-b050-4740-8db7-0ed11b980371',
            pinned=False,
            source='',
            type=EntityType.DOCUMENT_TYPE,
            visible_name='secret-algorithms.pdf'
        )

    def test_valid_metadata_with_root_as_parent_does_not_throw(self) -> None:
        Metadata(
            created_time=int(time.time() * 1000),
            last_modified=int(time.time() * 1000),
            new=False,
            parent='',
            pinned=False,
            source='',
            type=EntityType.DOCUMENT_TYPE,
            visible_name='secret-algorithms.pdf'
        )



    def test_negative_created_time_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=-1,
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("createdTime" in str(context.exception))


    def test_last_modified_in_far_future_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int((time.time() + 100000) * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("lastModified" in str(context.exception))

    def test_none_as_last_modified_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=None,
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("lastModified" in str(context.exception))


    def test_none_as_new_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=None,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("new" in str(context.exception))

    def test_string_as_new_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new='False',
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("new" in str(context.exception))

    def test_None_as_parent_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent=None,
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("parent" in str(context.exception))

    def test_invalid_uuid_as_parent_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='11-22-33',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("parent" in str(context.exception))

    def test_str_as_pinned_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned="False",
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("pinned" in str(context.exception))

    def test_none_as_source_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source=None,
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("source" in str(context.exception))

    def test_str_as_type_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type='DocumentType',
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("type" in str(context.exception))


    def test_none_as_visible_name_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataException) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name=None
            )
        self.assertTrue("visibleName" in str(context.exception))



    def test_metadata_to_dict_returns_excepted_content(self) -> None:

        time_now = int(time.time() * 1000)

        expected_dict = {
            "createdTime": time_now,
            "lastModified": time_now,
            "new": False,
            "parent": 'd433121d-b050-4740-8db7-0ed11b980371',
            "pinned": False,
            "source": '',
            "type": EntityType.COLLECTION_TYPE,
            "visibleName": 'secret_algorithms',
        }

        metadata = Metadata(
            created_time=expected_dict.get('createdTime'),
            last_modified=expected_dict.get('lastModified'),
            new=expected_dict.get('new'),
            parent=expected_dict.get('parent'),
            pinned=expected_dict.get('pinned'),
            source=expected_dict.get('source'),
            type=expected_dict.get('type'),
            visible_name=expected_dict.get('visibleName')
        )

        self.assertEqual(expected_dict, metadata.to_dict())


    def test_missing_positional_argument_raises_type_error(self) -> None:
        with self.assertRaises(TypeError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("parent" in str(context.exception))

