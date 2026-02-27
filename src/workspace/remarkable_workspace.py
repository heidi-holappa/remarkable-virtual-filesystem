"""
    Module for the functionalities of accessing
    reMarkable metadata content
"""

import copy
from typing import Dict, Any, Optional

from src.data.metadata_source import MetadataSource
from src.exception.constraint_violation_exception import ConstraintViolationException
from src.exception.invalid_metadata_exception import InvalidMetadataException
from src.exception.not_found_exception import NotFoundException
from src.exception.invalid_path_exception import InvalidPathException

from src.constant import ROOT_COLLECTION, COLLECTION_NOT_FOUND, INVALID_PATH
from src.dto.metadata import Metadata

class RemarkableWorkspace:
    """
        Class for accessing metadata content from
        reMarkable user collections
    """

    def __init__(self, source: MetadataSource):
        self._source = source
        self._data = self._source.load()
        self._current_collection = ''


    def get_data(self) -> Dict[str, Dict[str, Any]]:
        """
        A getter for the reMarkable filedata

        :return: a dictionary of Remarkable file data
        """
        return self._data


    def get_data_for_uuid(self, entry_uuid: str) -> Dict[str, Any]:
        """
        Returns the data for the provided UUID. If data
        is not found, raises a NotFoundException

        :return: a dictionary of metadata
        """

        data: Optional[Dict[str, Any]] = self._data.get(entry_uuid)

        if not data:
            raise NotFoundException(f"Metadata not found for {entry_uuid}")

        return data


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
        must be either an UUID of a CollectionType or an
        empty string for root.

        :return: None
        """
        is_root = collection == ''
        is_valid_collection = (self._data.get(collection)
                               and self._data[collection].get('type') == 'CollectionType')
        if not (is_root or is_valid_collection):
            raise NotFoundException(COLLECTION_NOT_FOUND)
        self._current_collection = collection


    def entry_is_a_collection(self, entity_uuid) -> bool:
        """
        Validates whether the metadata entry with the given UUID
        is of type CollectionType.

        Raises:
          - NotFoundException if a metadata entry for the given
            UUID is not found

        :param entity_uuid: UUID of the entry
        :return: boolean indicating whether this entry has type CollectionType
        """

        return self.get_data_for_uuid(entity_uuid).get('type') == 'CollectionType'


    def get_parent(self, entity_uuid: Optional[str] = None) -> str:
        """
        :param entity_uuid: optional uuid of an entity for which parent should be given
                        if no parameter is given, parent of current collection is returned
        :return: the parent of either the given entity or current collection. In case
                    parent is root or the current collection is root, an empty string is returned
        """

        if entity_uuid is None:
            entity_uuid = self._current_collection

        if not self._data.get(entity_uuid):
            raise NotFoundException(COLLECTION_NOT_FOUND)

        if entity_uuid == ROOT_COLLECTION or self._data.get(entity_uuid) == ROOT_COLLECTION:
            return ROOT_COLLECTION
        return self._data.get(entity_uuid).get('parent')

    def get_collection(self, collection: str, parent: str) -> Optional[str]:
        """
        As a first version returns the uuid of the collection with the given parent
        and a matching visible name
        :param collection: a name of the collection
        :param parent: UUID of the parent
        :return: an optional UUID of the collection
        """
        for k, v in self._data.items():
            if v.get('parent') != parent:
                continue
            if v.get('type') == 'CollectionType' and v.get('visibleName') == collection:
                return k
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

    def generate_absolute_collection_path(self, uuid: str) -> str:
        """
        A helper method to find the path for each entity.

        :param uuid: entity's uuid
        :param remarkable_metadata: a reference to the dictionary of metadata
        :return: a string representation of the path
        """

        if not self._data.get(uuid):
            return './<NA>'

        # print(f"data for {uuid}: {remarkable_metadata.get(uuid)}")
        if self._data[uuid].get('parent') == '':
            return "/" + self._data[uuid]['visibleName']

        if self._data[uuid].get('parent') == 'trash':
            return '/trash/' + self._data[uuid].get('visibleName')

        return (self.generate_absolute_collection_path(self._data[uuid]['parent']) +
                "/" + self._data[uuid].get('visibleName'))

    def change_collection(self, path: str) -> None:
        """
        Attempts to change current collection to the provided
        collection. If traversal of given path fails to locate
        a collection, InvalidPathException is raised.

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if collection could not be found
        """
        collection_pointer = self.traverse_path(path)
        if collection_pointer is None:
            raise InvalidPathException(INVALID_PATH)

        self._current_collection = collection_pointer

    def traverse_path(self, path: str) -> Optional[str]:
        """
        Splits the provided path into a list of entries and tries to
        traverse through the given path changes. At its simplest a path
        change can be traversing to one directory above the current position
        with '..' or into a direct subdirectory.

        See the project wiki for a comprehensive list of path changing rules.

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if collection could not be found
        """
        directory_changes: list[str] = path.split(sep="/")
        collection_pointer = self._current_collection
        if directory_changes[0] == '':
            # In absolute path traversal begins at root
            collection_pointer = ROOT_COLLECTION

        for directory in directory_changes:
            match directory:
                # No directory change
                case '' | '.':
                    continue
                # Traverse to parent
                case '..':
                    collection_pointer = self.get_parent(collection_pointer)
                # Traverse to descendant
                case _:
                    collection_pointer = self.get_collection(directory, collection_pointer)
            if collection_pointer is None:
                break

        return collection_pointer

    def handle_move_instruction(self, filename: str, path: str) -> None:
        """
        As an MVP the move instruction moves one DocumentType,
        i.e., changes the parent of the given DocumentType to the
        provided parent.

        In try-except following exceptions may occur:
          - InvalidPathException if target path does not exist
          - InvalidMetadataException if metadata validation fails
          - NotFoundException if the file to move is not found

        :param filename: name of the file to be moved
        :param path: the directory of the target parent
        :return: None
        """

        try:
            # Root path can not be moved
            if filename == "":
                raise ConstraintViolationException("Root path cannot be moved")

            # Handle possible path in filename
            if "/" in filename:
                parent_path, file = filename.rsplit(sep='/', maxsplit=1)
                parent_uuid = self.traverse_path(parent_path)
            else:
                file = filename
                parent_uuid = self._current_collection

            # Get the UUID of the new parent
            target_uuid: Optional[str] = self.traverse_path(path)
            if target_uuid is None:
                raise InvalidPathException(INVALID_PATH)


            # moving to the same parent should result in a no-op
            if parent_uuid == target_uuid:
                return

            # Get the metadata and UUID of the file in question
            entry_uuid: str = self.get_uuid_with_visible_name_and_parent(
                file, parent_uuid)

            if self.entry_is_a_collection(entry_uuid) and \
                self.is_target_path_descendant_of_source_path(target_uuid, entry_uuid):
                raise ConstraintViolationException("Collection can not be moved into itself or its descendant")

            if self.entry_is_a_collection(entry_uuid) and \
                self.exists_entry_with_same_visible_name_in_target_path(entry_uuid, target_uuid):
                raise ConstraintViolationException("Destination must not contain a child with the same name")


            new_metadata_entry: Dict[str, Any] = copy.deepcopy(self._data.get(entry_uuid))
            new_metadata_entry['parent'] = target_uuid

            # Create a Metadata DTO for given UUID
            metadata: Metadata = Metadata.from_dict(new_metadata_entry)

            # Call RemarkableSshMetadataSource to store the metadata entry
            self._source.write(entry_uuid, metadata)

            # Update local data
            self._data[entry_uuid] = new_metadata_entry

        except (NotFoundException,
                InvalidMetadataException,
                InvalidPathException,
                ConstraintViolationException) as e:
            print(f"ERROR: {e} ")

    def exists_entry_with_same_visible_name_in_target_path(self, entry_uuid: str, target_collection_uuid: str) -> bool:
        """
        Verifies whether an entry (either a Document or a Collection) with
        identical visibleName matching the visibleName of entry_uuid already
        exists in the target path.

        Raises:
          - NotFoundException if metadata for entry_uuid is not found

        :param entry_uuid: an entry of metadata
        :param target_collection_uuid: a target collection
        :return: True, if entry with identical visibleName exists
        """

        data: dict[str, Dict[str, Any]] = self.get_data()

        entry_visible_name: str = (self.get_data_for_uuid(entry_uuid)
                                   .get('visibleName'))

        for k, v in data.items():
            if (v.get('parent') == target_collection_uuid and
                    v.get('visibleName') == entry_visible_name):
                return True

        return False

    def is_target_path_descendant_of_source_path(self, target_path_uuid: str, source_path_uuid: str) -> bool:
        """
        Verifies that the given target path is not a descendant of the source path,
        i.e., the source path may not be an ancestor of the target path.

        :param source_path_uuid:
        :param target_path_uuid:
        :return:
        """

        collection_pointer: str = target_path_uuid

        while collection_pointer != '':
            if collection_pointer == source_path_uuid:
                return True
            collection_pointer = self.get_parent(collection_pointer)

        return False


    def get_uuid_with_visible_name_and_parent(self, filename: str, parent_uuid: str) -> str:
        """
        Gets the data for the given entry and composes a dictionary
        representation of the metadata. The entry is identified by
        the following rules:

          1. the visibleName of the entry is the filename
          2. the parent of the entry is the parent_uuid

        Note that the type of the entry is not consider, i.e., the entry
        may either be a DocumentType or a CollectionType.

        Raises:
          - NotFoundException, if no match is found

        :param filename: the visibleName of the entry
        :param parent_uuid: the parent of the entry
        :return: the UUID of the entry
        """

        print(f"filename: {filename}, parent: {parent_uuid}")

        for k, v in self._data.items():
            if v.get('parent') == parent_uuid:
                print(v.get('visibleName'))
            if v.get('parent') == parent_uuid and v.get('visibleName') == filename:
                return k

        path: Optional[str] = self.generate_absolute_collection_path(parent_uuid)
        raise NotFoundException(f"Metadata not found for {path}/{filename}")
