"""
    Module for metadata DTO tests
"""
import time
import unittest
from pydoc import visiblename

from src.dto.entry_type_enum import EntityType
from src.dto.metadata import Metadata
from src.exception import InvalidMetadataError


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
        with self.assertRaises(InvalidMetadataError) as context:
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
        with self.assertRaises(InvalidMetadataError) as context:
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
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=None, # type: ignore[arg-type]
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("lastModified" in str(context.exception))


    def test_none_as_new_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=None, # type: ignore[arg-type]
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("new" in str(context.exception))

    def test_string_as_new_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new='False', # type: ignore[arg-type]
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("new" in str(context.exception))

    def test_None_as_parent_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent=None,# type: ignore[arg-type]
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )

        self.assertTrue("parent" in str(context.exception))

    def test_invalid_uuid_as_parent_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
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
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned="False", # type: ignore[arg-type]
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("pinned" in str(context.exception))

    def test_none_as_source_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source=None, # type: ignore[arg-type]
                type=EntityType.DOCUMENT_TYPE,
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("source" in str(context.exception))

    def test_str_as_type_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type='DocumentType', # type: ignore[arg-type]
                visible_name='secret-algorithms.pdf'
            )
        self.assertTrue("type" in str(context.exception))


    def test_none_as_visible_name_raises_validation_exception(self) -> None:
        with self.assertRaises(InvalidMetadataError) as context:
            Metadata(
                created_time=int(time.time() * 1000),
                last_modified=int(time.time() * 1000),
                new=False,
                parent='d433121d-b050-4740-8db7-0ed11b980371',
                pinned=False,
                source='',
                type=EntityType.DOCUMENT_TYPE,
                visible_name=None # type: ignore[arg-type]
            )
        self.assertTrue("visibleName" in str(context.exception))



    def test_metadata_to_dict_returns_excepted_content(self) -> None:

        time_now = int(time.time() * 1000)

        created_time = time_now
        last_modified = time_now
        new = False
        parent = 'd433121d-b050-4740-8db7-0ed11b980371'
        pinned = False
        source = ''
        type_value = EntityType.COLLECTION_TYPE
        visiblename_value = 'secret_algorithms'

        expected_dict = {
            "createdTime": created_time,
            "lastModified": last_modified,
            "new": new,
            "parent": parent,
            "pinned": pinned,
            "source": source,
            "type": type_value,
            "visibleName": visiblename_value,
        }

        metadata = Metadata(
            created_time=created_time,
            last_modified=last_modified,
            new=new,
            parent=parent,
            pinned=pinned,
            source=source,
            type=type_value,
            visible_name=visiblename_value
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
            ) # type: ignore[call-arg]

        self.assertTrue("parent" in str(context.exception))

    def test_from_dict_raises_when_required_fields_are_missing(self) -> None:
        metadata_dict = {
            "createdTime": "123",
            "lastModified": "456",
            "new": False,
            "parent": "",
            "pinned": False,
            "source": "test",
            "type": "valid_type",
            # "visibleName" is intentionally missing
        }

        with self.assertRaises(InvalidMetadataError) as exc_info:
            Metadata.from_dict(metadata_dict)


        self.assertTrue("Missing metadata fields: visibleName" in str(exc_info.exception))

    def test_from_dict_raises_for_invalid_entity_type(self) -> None:
        metadata_dict = {
            "createdTime": "123",
            "lastModified": "456",
            "new": False,
            "parent": "",
            "pinned": False,
            "source": "test",
            "type": "not_a_valid_entity_type",
            "visibleName": "Test",
        }

        with self.assertRaises(InvalidMetadataError) as exc_info:
            Metadata.from_dict(metadata_dict)

        self.assertTrue("type: invalid value not_a_valid_entity_type" in str(exc_info.exception))