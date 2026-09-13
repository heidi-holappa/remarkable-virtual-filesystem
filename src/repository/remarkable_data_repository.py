from typing import Dict, List, Optional

from src.constant import (
    ROOT_COLLECTION,
    COLLECTION_NOT_FOUND,
    NOT_A_DIRECTORY)
from src.data.metadata_source_v2 import MetadataSourceV2
from src.exception import (
    RemarkableWriteError,
    NotFoundError,
    NoSuchDirectoryError,
    InvalidMetadataError)

from src.dto.entry import Entry
from src.dto.metadata import Metadata
from src.dto.content import Content

class RemarkableDataRepository:

    _in_memory_data: Dict[str, Entry]

    _current_collection: str
    _source: MetadataSourceV2

    def __init__(self, metadata_source: MetadataSourceV2) -> None:
        self._source = metadata_source
        self._in_memory_data = self._source.load()
        # Empty string is the root collection
        self._current_collection = ""


    def get_data(self) -> Dict[str, Entry]:
        """
        A getter for the reMarkable filedata

        :return: a dictionary of Remarkable file data
        """
        return self._in_memory_data

    def get_data_for_uuid(self, entry_uuid: str) -> Entry:
        """
        Returns the data for the provided UUID.

        Raises:
          - NotFoundError if data is not found

        :param entry_uuid: UUID of the entry
        :return: a data entry for collection or document
        """

        data: Optional[Entry] = self._in_memory_data.get(entry_uuid)

        if not data:
            raise NotFoundError(f"Metadata not found for {entry_uuid}")

        return data


    def get_visible_name_for_uuid(self, entity_uuid: str) -> str:
        """
        Returns the visibleName of the given entity. For root
        returns an empty string

        Raises:
          - NotFoundError if the entity is not found
          - InvalidMetadataError if visibleName is not an instance of str

        :param entity_uuid: UUID for a Document or Collection type
        :return: visible name of the entity
        """

        if entity_uuid == '':
            return ''

        data: Optional[Entry] = self._in_memory_data.get(entity_uuid)

        if not data:
            raise NotFoundError(f"Metadata not found for {entity_uuid}")

        visible_name = data.metadata.visible_name

        return visible_name

    def get_current_collection(self) -> str:
        """
        A getter for the current collection. An empty string
        represents the root.

        :return: a UUID of the current collection
        """
        return self._current_collection


    def set_current_collection(self, collection: str) -> None:
        """
        Setter for the current collection. The collection
        must be either a UUID of a CollectionType or an
        empty string for root.

        :param collection: UUID of the collection or an empty string for root

        raises:
          - NotFoundError: if collection is not found
        """
        is_root = collection == ''
        is_valid_collection = (self._in_memory_data.get(collection)
                               and self._in_memory_data[collection].metadata.type == 'CollectionType')
        if not (is_root or is_valid_collection):
            raise NotFoundError(COLLECTION_NOT_FOUND)
        self._current_collection = collection

    def get_parent(self, entity_uuid: Optional[str] = None) -> str:
        """
        raises:
          - NotFoundError: if parent is not found
          - InvalidMetadataError if field parent is not instance of str

        :param entity_uuid: optional uuid of an entity for which parent should be given
                        if no parameter is given, parent of current collection is returned
        :return: the parent of either the given entity or current collection. In case
                    parent is root or the current collection is root, an empty string is returned
        """

        if entity_uuid is None or not isinstance(entity_uuid, str):
            entity_uuid = self._current_collection

        entity_uuid_str = str(entity_uuid)

        if entity_uuid_str == ROOT_COLLECTION:
            return ROOT_COLLECTION

        if not self._in_memory_data.get(entity_uuid_str):
            raise NotFoundError(COLLECTION_NOT_FOUND)

        candidate: Entry = self._in_memory_data[entity_uuid_str]

        parent = candidate.metadata.parent

        return parent

    def get_collection(self, file_name: str, parent: str) -> Optional[str]:
        """
        Returns the UUID of the collection with the given
        parent and a matching visible name

        raises:
          - NoSuchDirectoryError: if only match for a segment of a path is a DocumentType (file)

        :param file_name: a name of the collection
        :param parent: UUID of the parent
        :return: an optional UUID of the collection
        """
        has_document_type_with_given_file_name: bool = False

        for entry_uuid, entry in self._in_memory_data.items():
            if entry.metadata.parent != parent:
                continue
            if entry.metadata.type == 'CollectionType' and entry.metadata.visible_name == file_name:
                return entry_uuid
            if entry.metadata.visible_name == file_name:
                has_document_type_with_given_file_name = True
        if has_document_type_with_given_file_name:
            raise NoSuchDirectoryError(f'{file_name}: {NOT_A_DIRECTORY}')

        return None

    def get_current_path(self) -> str:
        """
        Get a human-readable bash-esque representation for the
        current collection

        :return: a string representing the current collection as a bash-path
        """
        if self._current_collection == '':
            return "/"
        return self.generate_absolute_collection_path(self._current_collection)

    def generate_absolute_collection_path(self, item_uuid: str) -> str:
        """
        A helper method to find the path for each entity.

        :param item_uuid: entity's uuid
        :return: a string representation of the path
        """

        if item_uuid == ROOT_COLLECTION:
            return "/"

        if not self._in_memory_data.get(item_uuid):
            return './<NA>'

        entry: Entry = self._in_memory_data[item_uuid]
        parent = entry.metadata.parent
        visible_name = entry.metadata.visible_name


        if parent == '':
            return "/" + visible_name

        if self._in_memory_data[item_uuid].metadata.parent == 'trash':
            return '/trash/' + visible_name

        return self.generate_absolute_collection_path(parent) + "/" + visible_name



    def refresh_data(self) -> None:
        """
        Provides other layers an option to invoke
        refresh of in-memory data
        """
        self._in_memory_data = self._source.load()

        
    def write_metadata(self, entry_uuid: str, metadata: Metadata) -> None:
        """
        Attempts to write new metadata for an entry with the provided
        UUID. The write operation is done to both target machine data
        and in-memory data (in this order, so failure to update target
        metadata aborts operation).

        raises:
          **NotFoundError**: if entry is not found
          **RemarkableWriteError**: if write operation to target machine fails

        :param entry_uuid: the UUID of the entry
        :param metadata: metadata to write to the entry
        """

        if entry_uuid not in self._in_memory_data:
            raise NotFoundError("No entry found for uuid %s", entry_uuid)

        self._source.write_metadata(entry_uuid, metadata)
        self._in_memory_data[entry_uuid].metadata = metadata


    def get_metadata_for_uuid(self, entry_uuid: str) -> Metadata:
        """
        Attempts to get metadata for the given UUID.

        Raises:
            NotFoundError if no entry is found

        :param entry_uuid: identification for the entry
        """

        if entry_uuid not in self._in_memory_data:
            raise NotFoundError("No entry found for uuid %s", entry_uuid)

        return self._in_memory_data[entry_uuid].metadata



    def remove_entry(self, entry_uuid: str) -> None:
        """
        Attempts to remove an entry with the given UUID.

        Raises:
            NotFoundError if no entry is found with the UUID

        :param entry_uuid: entry to remove
        """
        if entry_uuid not in self._in_memory_data:
            raise NotFoundError("No entry found for uuid %s", entry_uuid)

        self._in_memory_data.pop(entry_uuid)


    def restart_xochitl(self) -> None:
        """
        Invokes source method handling restart
        of xochitl GUI application

        Raises:
            may pass towards RemarkableOperationException
            raised by the source in case subprocess fails
        """

        self._source.restart_xochitl()



    def invoke_remote_copy(self,
                           source_file: str,
                           metadata: Metadata,
                           content: Content) -> None:
        """
        Invokes remote copy operation to the source

        :param source_file: the host source to copy
        :param metadata: metadata entry for the new entry
        :param content: content for the new entry
        """

        self._source.remote_copy(source_file=source_file,
                                 metadata=metadata, content=content)



    def remove_entities(self, entity_uuids: List[str]) -> None:
        """
        Attempts to remove the provided entity from the reMarkable
        tablet.

        :param entity_uuids: UUID of the entity to remove
        """

        try:
            self._source.remove(entity_uuids)
        except RemarkableWriteError as e:
            print(f"ERROR: {e}")


