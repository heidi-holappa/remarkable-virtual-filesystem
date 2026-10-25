"""
Abstract base class for commands.
"""
from abc import ABC, abstractmethod
from fnmatch import fnmatchcase
import time
import uuid

from src.dto.metadata import Metadata
from src.dto.entry import Entry
from src.dto.entry_type_enum import EntityType

from src.constant import (
    ROOT_COLLECTION,
    NO_SUCH_FILE_OR_DIRECTORY,
    PARENT_NOT_FOUND)
from src.exception import NotFoundError, InvalidPathError
from src.repository.remarkable_data_repository import RemarkableDataRepository


class BaseCommand(ABC):
    """
    Abstract base class for commands. Each command
    extends BaseCommand and implements the handle
    method.
    """

    def __init__(self, repository: RemarkableDataRepository) -> None:
        self._repository = repository

    @abstractmethod
    def handle(self, args: list[str]) -> None:
        """
        each command class specializes on handling
        a specific command.

        :param args: a list of arguments for the command
        """

    # --------------------------
    #  Shared methods
    # --------------------------

    def _traverse_path(self, path: str) -> str | None:
        """
        Splits the provided path into a list of entries and tries to
        traverse through the given path changes. At its simplest a path
        change can be traversing to one directory above the current position
        with '..' or into a direct subdirectory.

        See the project wiki for a comprehensive list of path changing rules.

        raises:
          - `NoSuchDirectoryError`: if the only match is a DocumentType (file)
          - `NotFoundError`: if parent is not found

        :param path: a string representation of a path
        :return: an optional uuid of the target collection or None if
                    collection could not be found
        """
        directory_changes: list[str] = path.split(sep="/")
        collection_pointer: str | None = self._repository.get_current_collection()

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
                    collection_pointer = self._repository.get_parent(collection_pointer)
                # Traverse to descendant
                case _:
                    if not isinstance(collection_pointer, str):
                        break
                    collection_pointer = self._repository.get_collection(
                        directory, collection_pointer)
            if collection_pointer is None:
                break
        return collection_pointer


    def _resolve_source_parent_and_visible_name(self, source: str) -> tuple[str, str]:
        """
        Resolves the parent for an entity with a matching visible name
        or for multiple entities matching a wild card.

        Raises:
            - NotFoundError if the parent can not be resolved
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
                raise NotFoundError(f"cannot move {source}: {NO_SUCH_FILE_OR_DIRECTORY}")
        else:
            visible_name = source
            parent_uuid = self._repository.get_current_collection()

        return visible_name, parent_uuid


    def _get_matches_for_wildcard(self, parent_uuid: str, wildcard: str) -> list[str]:
        """
        Finds all entries with the provided parent and visibleName
        that matches the given wildcard.

        Raises:
            - NotFoundError if the parent UUID is not found

        :param parent_uuid:
        :param wildcard:
        :return: a list of entry UUIDs matching the wildcard or an
                    empty list, if no matches are found
        """

        try:
            if not self._entry_is_a_collection(parent_uuid):
                raise NotFoundError(PARENT_NOT_FOUND.format(
                    parent=parent_uuid, entity=wildcard))
        except NotFoundError as e:
            raise NotFoundError(
                PARENT_NOT_FOUND.format(parent=parent_uuid, entity=wildcard)) from e


        wildcard_matches: list[str] = []

        for entry_uuid, entry in self._repository.get_data().items():
            has_matching_visible_name: bool = self._visible_name_matches_wildcard(
                wildcard, entry.metadata.visible_name)
            if entry.metadata.parent == parent_uuid and has_matching_visible_name:
                wildcard_matches.append(entry_uuid)

        return wildcard_matches


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
          - NotFoundError, if no match is found

        :param filename: the visibleName of the entry
        :param parent_uuid: the parent of the entry
        :return: the UUID of the entry
        """

        # print(f"filename: {filename}, parent: {parent_uuid}")

        for entry_uuid, entry in self._repository.get_data().items():
            # if v.get('parent') == parent_uuid:
                # print(v.get('visibleName'))
            if (entry.metadata.parent == parent_uuid and
                    entry.metadata.visible_name == filename):
                return entry_uuid

        path_prefix = ""
        if parent_uuid != ROOT_COLLECTION:
            path: str | None = self._repository.generate_absolute_collection_path(parent_uuid)
            if path:
                path_prefix = f"{path}"
        raise NotFoundError(f"cannot access {path_prefix}/{filename}: "
                                f"{NO_SUCH_FILE_OR_DIRECTORY}")


    def _entry_is_a_collection(self, entity_uuid: str) -> bool:
        """
        Validates whether the metadata entry with the given UUID
        is of type CollectionType.

        Raises:
          - NotFoundError if a metadata entry for the given
            UUID is not found

        :param entity_uuid: UUID of the entry
        :return: boolean indicating whether this entry has type CollectionType
        """

        if entity_uuid == ROOT_COLLECTION:
            return True

        metadata: Metadata = self._repository.get_metadata_for_uuid(entity_uuid)

        return metadata.type == EntityType.COLLECTION_TYPE

    def _exists_visible_name_in_collection(
            self, entry_uuid: str, target_collection_uuid: str) -> bool:
        """
        Verifies whether an entry (either a Document or a Collection) with
        identical visibleName matching the visibleName of entry_uuid already
        exists in the target path.

        Raises:
          - NotFoundError if metadata for entry_uuid is not found

        :param entry_uuid: an entry of metadata
        :param target_collection_uuid: a target collection
        :return: True, if entry with identical visibleName exists
        """

        entry: Entry = self._repository.get_data_for_uuid(entry_uuid)
        entry_visible_name: str = entry.metadata.visible_name

        return self._has_visible_name_equal_to_entry_uuid_in_collection(
            entry_uuid, entry_visible_name, target_collection_uuid)

    def _has_visible_name_equal_to_entry_uuid_in_collection(
            self, entry_uuid: str, visible_name: str, target_collection_uuid: str) -> bool:
        """
        Verifies whether an entry (either a Document or a Collection) with
        identical visibleName matching the visibleName of entry_uuid already
        exists in the target path.

        Raises:
          - NotFoundError if metadata for entry_uuid is not found

        :param entry_uuid: an entry of metadata
        :param visible_name: visible name to search for
        :param target_collection_uuid: a target collection
        :return: True, if entry with identical visibleName exists
        """

        data: dict[str, Entry] = self._repository.get_data()

        for e_uuid, entry in data.items():
            if e_uuid == entry_uuid:
                continue
            if (entry.metadata.parent == target_collection_uuid and
                    entry.metadata.visible_name == visible_name):
                return True

        return False

    @staticmethod
    def _visible_name_matches_wildcard(pattern: str, visible_name: str) -> bool:
        """
        Verifies whether the provided visibleName matches with the given wildcard.

        :param pattern: A string with a wildcard symbol '*'
        :param visible_name: visibleName of an entry
        :return: boolean indication whether it is a match
        """

        return fnmatchcase(visible_name, pattern)


    def _get_descendant_uuids(self, entity_uuid: str) -> list[str]:
        """
        Collects UUIDs of all descendants for the given entity_uuid.

        Raises:
          - InvalidPathError if the given UUID is not a valid
            UUID for a CollectionType metadata entry.

        :param entity_uuid: a UUID for a CollectionType
        :return: a list of entity UUIDs
        """

        if not self._entry_is_a_collection(entity_uuid):
            raise InvalidPathError(f"Metadata for CollectionType not found: {entity_uuid}")

        descendants: list[str] = []

        for k in self._repository.get_data().keys():
            if self._repository.get_parent(k) == entity_uuid:
                descendants.append(k)
                if self._entry_is_a_collection(k):
                    descendants.extend(self._get_descendant_uuids(k))

        return descendants


    def _create_collection_metadata_and_invoke_write(self, parent: str, path_name: str) -> str:
        """
        Creates metadata for a new collection and attempts to invoke
        a write operation for reMarkable reader. reMarkable is lax
        regarding rules for naming. For instance, nothing prevents
        two entries with the same parent to have the same visible name.
        This method does no validation and instead just perpares a
        Metadata entry and attempts to write it. Callee must take
        any possible validation into consideration.

        Raises: RemarkableWriteError in case write operation
                fails. Callee must handle the possible exception

        :param parent: UUID of the parent collection
        :param path_name: visible name of the new path

        :return: UUID of the new created collection.

        """

        metadata: Metadata = Metadata(
            created_time=int(time.time()),
            last_modified=int(time.time()),
            new=False,
            parent=parent,
            pinned=False,
            source="",
            type=EntityType.COLLECTION_TYPE,
            visible_name=path_name
        )

        # Generate a random UUID for the new entry
        path_uuid: str = str(uuid.uuid4())

        self._repository.create_entry_if_absent(path_uuid, metadata)

        self._repository.write_metadata(path_uuid, metadata)

        return path_uuid


    def _parent_has_child_path_with_given_name(
            self, parent_uuid: str, child_visible_name: str) -> bool:
        """
        Verifies, whether the provided parent UUID has a child collection
        with the given visibleName.

        :param parent_uuid: UUID of the parent collection
        :param child_visible_name: visibleName of the child
        :rtype: bool indication of whether child exists
        """

        for entry in self._repository.get_data().values():
            if (entry.metadata.type == EntityType.COLLECTION_TYPE and
                    entry.metadata.parent == parent_uuid and
                    entry.metadata.visible_name == child_visible_name):
                return True

        return False


    def _collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(
            self, visible_name: str, parent_uuid: str) -> list[str]:
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

        entities_to_write: list[str] = []

        if '*' in visible_name:
            entities_to_write.extend(
                self._get_matches_for_wildcard(parent_uuid, visible_name)
            )
            for entry_uuid in entities_to_write:
                if self._entry_is_a_collection(entry_uuid):
                    entities_to_write.extend(self._get_descendant_uuids(entry_uuid))
        else:
            # Get the metadata and UUID of the file in question
            entity_uuid: str = self._get_uuid_with_visible_name_and_parent(
                visible_name, parent_uuid)
            entities_to_write.append(entity_uuid)
            if self._entry_is_a_collection(entity_uuid):
                entities_to_write.extend(self._get_descendant_uuids(entity_uuid))

        return entities_to_write
