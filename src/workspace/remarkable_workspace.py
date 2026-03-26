"""
    Module for the functionalities of accessing
    reMarkable metadata content
"""

import copy
from fnmatch import fnmatchcase
from typing import Dict, List, Tuple, Any, Optional

from src.data.metadata_source import MetadataSource
from src.exception.constraint_violation_exception import ConstraintViolationException
from src.exception.invalid_metadata_exception import InvalidMetadataException
from src.exception.no_such_file_or_directory_exception import NoSuchFileOrDirectoryException
from src.exception.not_a_directory_exception import NotADirectoryException
from src.exception.not_found_exception import NotFoundException
from src.exception.invalid_path_exception import InvalidPathException

from src.constant import ROOT_COLLECTION, COLLECTION_NOT_FOUND, INVALID_PATH, PARENT_NOT_FOUND, NOT_A_DIRECTORY, \
    NO_SUCH_FILE_OR_DIRECTORY, LS_COLUMN_WIDTH
from src.dto.metadata import Metadata
from src.exception.remarkable_write_exception import RemarkableWriteException


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
        Returns the data for the provided UUID.

        Raises:
          - NotFoundException if data is not found

        :return: a dictionary of metadata
        """

        data: Optional[Dict[str, Any]] = self._data.get(entry_uuid)

        if not data:
            raise NotFoundException(f"Metadata not found for {entry_uuid}")

        return data

    def get_visible_name_for_uuid(self, entity_uuid: str) -> str:
        """
        Returns the visibleName of the given entity.

        Raises:
          - NotFoundException if the entity is not found

        :param entity_uuid: UUID for a Document or Collection type
        :return: visible name of the entity
        """

        data: Optional[Dict[str, Any]] = self._data.get(entity_uuid)

        if not data:
            raise NotFoundException(f"Metadata not found for {entity_uuid}")

        return data.get('visibleName')




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

        raises:
          - NotFoundException: if collection is not found

        :return: None
        """
        is_root = collection == ''
        is_valid_collection = (self._data.get(collection)
                               and self._data[collection].get('type') == 'CollectionType')
        if not (is_root or is_valid_collection):
            raise NotFoundException(COLLECTION_NOT_FOUND)
        self._current_collection = collection


    def get_parent(self, entity_uuid: Optional[str] = None) -> str:
        """
        raises:
          - NotFoundException: if parent is not found

        :param entity_uuid: optional uuid of an entity for which parent should be given
                        if no parameter is given, parent of current collection is returned
        :return: the parent of either the given entity or current collection. In case
                    parent is root or the current collection is root, an empty string is returned
        """

        if entity_uuid is None:
            entity_uuid = self._current_collection

        if entity_uuid == ROOT_COLLECTION or self._data.get(entity_uuid) == ROOT_COLLECTION:
            return ROOT_COLLECTION

        if not self._data.get(entity_uuid):
            raise NotFoundException(COLLECTION_NOT_FOUND)

        return self._data.get(entity_uuid).get('parent')

    def get_collection(self, file_name: str, parent: str) -> Optional[str]:
        """
        Returns the UUID of the collection with the given
        parent and a matching visible name

        raises:
          - NotADirectoryException: if only match for a segment of a path is a DocumentType (file)

        :param file_name: a name of the collection
        :param parent: UUID of the parent
        :return: an optional UUID of the collection
        """
        has_document_type_with_given_file_name: bool = False
                
        for k, v in self._data.items():
            if v.get('parent') != parent:
                continue
            if v.get('type') == 'CollectionType' and v.get('visibleName') == file_name:
                return k
            if v.get('visibleName') == file_name:
                has_document_type_with_given_file_name = True
        if has_document_type_with_given_file_name:
            raise NotADirectoryException(f'{file_name}: {NOT_A_DIRECTORY}')

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

        if uuid == ROOT_COLLECTION:
            return "/"

        if not self._data.get(uuid):
            return './<NA>'

        # print(f"data for {uuid}: {remarkable_metadata.get(uuid)}")
        if self._data[uuid].get('parent') == '':
            return "/" + self._data[uuid]['visibleName']

        if self._data[uuid].get('parent') == 'trash':
            return '/trash/' + self._data[uuid].get('visibleName')

        return (self.generate_absolute_collection_path(self._data[uuid]['parent']) +
                "/" + self._data[uuid].get('visibleName'))

    def process_ls(self) -> None:

        remarkable_metadata = self.get_data()

        list_result: List[str] = []
        collections: List[Tuple[str, str]] = []
        documents: List[Tuple[str, str]] = []


        collection_uuid = self.get_current_collection()

        if not collection_uuid == ROOT_COLLECTION:
            list_result.append(f"{' '*LS_COLUMN_WIDTH}../")
        list_result.append(f"{' '*LS_COLUMN_WIDTH}./")

        for uuid, v in remarkable_metadata.items():
            if v.get('parent') != self.get_current_collection():
                continue
            if v.get('type') == 'CollectionType':
                collections.append((f"{v.get('visibleName')}/", f"{v.get('size')}"))
            elif v.get('type') == 'DocumentType':
                documents.append((f"{v.get('visibleName')}", f"{v.get('size')}"))
            else:
                print(f"ls: entry is neither a file or a directory: {uuid}")

        for t in sorted(collections, key=lambda x: x[0].lower()):
            name, size = t
            padding: str = ' '*(LS_COLUMN_WIDTH - len(size))
            list_result.append(f"{size}{padding}{name}")

        for t in sorted(documents, key=lambda x: x[0].lower()):
            name, size = t
            padding: str = ' ' * (LS_COLUMN_WIDTH - len(size))
            list_result.append(f"{size}{padding}{name}")

        size_header = "size (kB)"
        header_padding = " "*(LS_COLUMN_WIDTH - len(size_header))
        name_header = "name"
        header = f"{size_header}{header_padding}{name_header}"
        print(header)
        for entry in list_result:
            print(entry)


    def change_collection(self, path: str) -> None:
        """
        Attempts to change current collection to the provided
        collection. If traversal of given path fails to locate
        a collection, InvalidPathException is raised.

        raises:
          - NotADirectoryException: instead of passing the raised exception a
          new one is thrown to include the full path in error message
          - NoSuchFileOrDirectoryException: no matching file or directory was found

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if collection could not be found
        """


        try:
            collection_pointer = self._traverse_path(path)
        except NotADirectoryException as e:
            raise NotADirectoryException(f"{path}: {NOT_A_DIRECTORY}")
        if collection_pointer is None:
            raise NoSuchFileOrDirectoryException(f"{path}: {NO_SUCH_FILE_OR_DIRECTORY}")

        self._current_collection = collection_pointer

    def process_move_command(self, source: str, path: str) -> None:
        """
        A single move instruction moves one or several entities
        with a common parent to the provided target path. This
        method prepares a list of source entities to be moved
        and then separately invokes a helper method to handle
        the move operation for each entity. The list of entries
        will be sorted in alphabetical order based on the visible
        names of the entities.

        In try-except following exceptions may occur:
          - InvalidPathException if target path does not exist
          - InvalidMetadataException if metadata validation fails
          - NotFoundException if the file to move is not found

        :param source: name of the file to be moved
        :param path: the directory of the target parent
        :return: None
        """

        try:
            # Root path can not be moved
            if source == "":
                raise ConstraintViolationException("root path cannot be moved")

            # Attempt to resolve the target UUID
            # from the provided target path
            target_uuid: Optional[str] = self._traverse_path(path)
            if target_uuid is None:
                raise InvalidPathException(f'{path}: {NO_SUCH_FILE_OR_DIRECTORY}')

            visible_name, parent_uuid = self._resolve_source_parent_and_visible_name(source)

            # attempt to move entities to the same parent
            # should result in a no-op
            if parent_uuid == target_uuid:
                return

            entities_to_move: List[str] =  self._collect_uuids_for_children_matching_name_or_pattern(
                visible_name, parent_uuid)

            if not entities_to_move:
                raise NotFoundException(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}")

            for entity in entities_to_move:
                self._move_entity(entity, target_uuid)

        except (ConstraintViolationException,
                InvalidPathException,
                NotFoundException) as e:
            print(f"mv: {e} ")

    def process_remove_command(self, target_pattern: str) -> None:
        """
        A remove command removes one or several entities
        (documents and/or collections) matching the provided
        pattern from the reMarkable device.

        Handles following exceptions and informs user of an error:
          - NotFoundException if source path is not found
          - KeyError: if UUID is not found for data to be removed

        :param target_pattern: pattern for sources to be removed
        :return: None
        """

        try:
            visible_name, parent_uuid = self._resolve_source_parent_and_visible_name(target_pattern)

            entities_to_remove: List[str] = self._collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(
                visible_name, parent_uuid)

            self._remove_entities(entities_to_remove)

            for uuid in entities_to_remove:
                self._data.pop(uuid)

        except (NotFoundException, KeyError) as e:
            print(f"ERROR: {e}")

    # ----------------------------------
    # private methods
    # ----------------------------------


    def _resolve_source_parent_and_visible_name(self, source: str) -> Tuple[str, str]:
        """
        Resolves the parent for an entity with a matching visible name
        or for multiple entities matching a wild card.

        Raises:
            - NotFoundException if the parent can not be resolved
                when path is provided with the source

        :param source: a source for one or several entities
        :return: a tuple containing the visible name or a wild card
                    for entity/entities with the parent returned
        """
        # Handle possible path in filename
        if "/" in source:
            parent_path, visible_name = source.rsplit(sep='/', maxsplit=1)
            parent_uuid = self._traverse_path(parent_path)
            if parent_uuid is None:
                raise NotFoundException(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}")
        else:
            visible_name = source
            parent_uuid = self._current_collection

        return visible_name, parent_uuid

    def _collect_uuids_for_children_matching_name_or_pattern(self, visible_name: str, parent_uuid: str) -> List[str]:
        """
        Collects the UUIDs of all children with the provided
        parent collection matching a visible name or a pattern.

        :param visible_name: an exact match to a visible name
                                or a pattern to match against
        :param parent_uuid: parent of the entity or entities
        :return: list of entities on which a write operation
                    is to be executed
        """

        entities_to_write: List[str] = []

        if '*' in visible_name:
            entities_to_write.extend(
                self._get_matches_for_wildcard(parent_uuid, visible_name)
            )
        else:
            # Get the metadata and UUID of the file in question
            entity_uuid: str = self._get_uuid_with_visible_name_and_parent(
                visible_name, parent_uuid)
            entities_to_write.append(entity_uuid)

        return entities_to_write


    def _collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(self, visible_name: str, parent_uuid: str) -> List[str]:
        """
        Collects the UUIDs of all children with the provided
        parent collection matching a visible name or a pattern.
        In addition, also collects all the descendants of
        matching CollectionTypes

        :param visible_name: an exact match to a visible name
                                or a pattern to match against
        :param parent_uuid: parent of the entity or entities
        :return: list of entities on which a write operation
                    is to be executed
        """

        entities_to_write: List[str] = []

        if '*' in visible_name:
            entities_to_write.extend(
                self._get_matches_for_wildcard(parent_uuid, visible_name)
            )
            for entity_uuid in entities_to_write:
                if self._entry_is_a_collection(entity_uuid):
                    entities_to_write.extend(self._get_descendant_uuids(entity_uuid))
        else:
            # Get the metadata and UUID of the file in question
            entity_uuid: str = self._get_uuid_with_visible_name_and_parent(
                visible_name, parent_uuid)
            entities_to_write.append(entity_uuid)
            if self._entry_is_a_collection(entity_uuid):
                entities_to_write.extend(self._get_descendant_uuids(entity_uuid))

        return entities_to_write

    def _get_descendant_uuids(self, entity_uuid: str) -> List[str]:
        """
        Collects UUIDs of all descendants for the given entity_uuid.

        Raises:
          - InvalidPathException if the given UUID is not a valid
            UUID for a CollectionType metadata entry.

        :param entity_uuid: a UUID for a CollectionType
        :return: a list of entity UUIDs
        """

        if not self._entry_is_a_collection(entity_uuid):
            raise InvalidPathException(f"Metadata for CollectionType not found: {entity_uuid}")

        descendants: List[str] = []

        for k in self.get_data().keys():
            if self.get_parent(k) == entity_uuid:
                descendants.append(k)
                if self._entry_is_a_collection(k):
                    descendants.extend(self._get_descendant_uuids(k))

        return descendants

    def _traverse_path(self, path: str) -> Optional[str]:
        """
        Splits the provided path into a list of entries and tries to
        traverse through the given path changes. At its simplest a path
        change can be traversing to one directory above the current position
        with '..' or into a direct subdirectory.

        See the project wiki for a comprehensive list of path changing rules.

        raises:
          - `NotADirectoryException`: if the only match is a DocumentType (file)
          - `NotFoundException`: if parent is not found

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if
                    collection could not be found
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

    def _move_entity(self, entity_uuid: str, target_uuid: str) -> None:
        """
        Sets the parent of the provided entity to be the
        target UUID

        :param entity_uuid: entity which parent is updated
        :param target_uuid: the new parent of the entity
        :return: None
        """

        try:
            if self._entry_is_a_collection(entity_uuid) and \
                self._is_target_path_descendant_of_source_path(target_uuid, entity_uuid):
                raise ConstraintViolationException(
                    "collection can not be moved into itself or its descendant")

            if self._entry_is_a_collection(entity_uuid) and \
                self._exists_entry_with_same_visible_name_in_target_path(entity_uuid, target_uuid):
                raise ConstraintViolationException(
                    f"destination must not contain a child with the same name: "
                    f"{self.get_visible_name_for_uuid(entity_uuid)}")

            new_metadata_entry: Dict[str, Any] = copy.deepcopy(self._data.get(entity_uuid))
            new_metadata_entry['parent'] = target_uuid

            # Create a Metadata DTO for given UUID
            metadata: Metadata = Metadata.from_dict(new_metadata_entry)

            # Call RemarkableSshMetadataSource to store the metadata entry
            self._source.write(entity_uuid, metadata)

            # Update local data
            self._data[entity_uuid] = new_metadata_entry

        except (NotFoundException,
                InvalidMetadataException,
                ConstraintViolationException,
                RemarkableWriteException) as e:
            print(f"mv: {e} ")


    def _remove_entities(self, entity_uuids: List[str]) -> None:
        """
        Attempts to remove the provided entity from the reMarkable
        tablet.

        :param entity_uuid: UUID of the entity to remove
        :return: None
        """

        try:
            self._source.remove(entity_uuids)
        except RemarkableWriteException as e:
            print(f"ERROR: {e}")


    def _get_matches_for_wildcard(self, parent_uuid: str, wildcard: str) -> List[str]:
        """
        Finds all entries with the provided parent and visibleName
        that matches the given wildcard.

        Raises:
            - NotFoundException if the parent UUID is not found

        :param parent_uuid:
        :param wildcard:
        :return: a list of entry UUIDs matching the wildcard or an
                    empty list, if no matches are found
        """

        try:
            if not self._entry_is_a_collection(parent_uuid):
                raise NotFoundException(PARENT_NOT_FOUND.format(parent=parent_uuid, entity=wildcard))
        except NotFoundException:
            raise NotFoundException(PARENT_NOT_FOUND.format(parent=parent_uuid, entity=wildcard))


        wildcard_matches: List[str] = []

        for k, v in self.get_data().items():
            has_matching_visible_name: bool = self._visible_name_matches_wildcard(
                wildcard, v.get('visibleName'))
            if v.get('parent') == parent_uuid and has_matching_visible_name:
                wildcard_matches.append(k)

        return wildcard_matches

    @staticmethod
    def _visible_name_matches_wildcard(pattern: str, visible_name: str) -> bool:
        """
        Verifies whether the provided visibleName matches with the given wildcard.

        :param pattern: A string with a wildcard symbol '*'
        :param visible_name: visibleName of an entry
        :return: boolean indication whether it is a match
        """

        return fnmatchcase(visible_name, pattern)

    def _exists_entry_with_same_visible_name_in_target_path(
            self, entry_uuid: str, target_collection_uuid: str) -> bool:
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

        for v in data.values():
            if (v.get('parent') == target_collection_uuid and
                    v.get('visibleName') == entry_visible_name):
                return True

        return False

    def _is_target_path_descendant_of_source_path(
            self, target_path_uuid: str, source_path_uuid: str) -> bool:
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


    def _get_uuid_with_visible_name_and_parent(self, filename: str, parent_uuid: str) -> str:
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

        # TODO: make this a debug level log entry
        # print(f"filename: {filename}, parent: {parent_uuid}")

        for k, v in self._data.items():
            # TODO: this could be debug level log entry too
            # if v.get('parent') == parent_uuid:
                # print(v.get('visibleName'))
            if v.get('parent') == parent_uuid and v.get('visibleName') == filename:
                return k

        path_prefix = ""
        if parent_uuid != ROOT_COLLECTION:
            path: Optional[str] = self.generate_absolute_collection_path(parent_uuid)
            if path:
                path_prefix = f"{path}"
        raise NotFoundException(f"cannot access {path_prefix}/{filename}: {NO_SUCH_FILE_OR_DIRECTORY}")

    def _entry_is_a_collection(self, entity_uuid) -> bool:
        """
        Validates whether the metadata entry with the given UUID
        is of type CollectionType.

        Raises:
          - NotFoundException if a metadata entry for the given
            UUID is not found

        :param entity_uuid: UUID of the entry
        :return: boolean indicating whether this entry has type CollectionType
        """

        if entity_uuid == ROOT_COLLECTION:
            return True

        return self.get_data_for_uuid(entity_uuid).get('type') == 'CollectionType'
