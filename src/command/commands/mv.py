"""
Implementation of move command
"""

import copy

from src.dto.metadata import Metadata
from src.exception import (
    ConstraintViolationError,
    NotFoundError,
    InvalidPathError,
    InvalidMetadataError,
    RemarkableWriteError)
from src.constant import  NO_SUCH_FILE_OR_DIRECTORY
from .base_command import BaseCommand

# pylint: disable=too-few-public-methods
class MoveCommand(BaseCommand):
    """
    Implementation of move command
    """

    def handle(self, args: list[str]) -> None:
        """
        A light implementation of move command

        Usage examples:
          - mv a.pdf /foo
          - mv *.pdf ./bar

        :param args: arguments given for the instruction
        """
        if len(args) == 2:
            operand_source, operand_target = args
            self._process_move_command(
                operand_source=operand_source, operand_target=operand_target)
        else:
            print("Usage (mvp): mv <filename without path> <path>")

    def _process_move_command(self, operand_source: str, operand_target: str) -> None:
        """
        A single move instruction moves one or several entities
        with a common parent to the provided target path. This
        method prepares a list of source entities to be moved
        and then separately invokes a helper method to handle
        the move operation for each entity. The list of entries
        will be sorted in alphabetical order based on the visible
        names of the entities.

        In try-except following exceptions may occur:
          - InvalidPathError if target path does not exist
          - InvalidMetadataError if metadata validation fails
          - NotFoundError if the file to move is not found

        :param operand_source: name of the file to be moved
        :param operand_target: the directory of the target parent
        """

        try:
            # Root path can not be moved
            if operand_source == "":
                raise ConstraintViolationError("root path cannot be moved")

            # Attempt to resolve the target UUID
            # from the provided target path
            target_uuid: str | None = self._traverse_path(operand_target)
            if target_uuid is None:
                raise InvalidPathError(f'{operand_target}: {NO_SUCH_FILE_OR_DIRECTORY}')

            visible_name, parent_uuid = self._resolve_source_parent_and_visible_name(operand_source)

            # attempt to move entities to the same parent
            # should result in a no-op
            if parent_uuid == target_uuid:
                return

            entities_to_move: list[str] =  (
                self._collect_uuids_for_children_matching_name_or_pattern(
                visible_name, parent_uuid))

            if not entities_to_move:
                raise NotFoundError(
                    f"cannot move {operand_source}: {NO_SUCH_FILE_OR_DIRECTORY}")

            for entity in entities_to_move:
                self._move_entity(entity, target_uuid)

        except (ConstraintViolationError,
                InvalidPathError,
                NotFoundError) as e:
            print(f"mv: {e} ")


    def _collect_uuids_for_children_matching_name_or_pattern(
            self, visible_name: str, parent_uuid: str) -> list[str]:
        """
        Collects the UUIDs of all children with the provided
        parent collection matching a visible name or a pattern.

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
        else:
            # Get the metadata and UUID of the file in question
            entity_uuid: str = self._get_uuid_with_visible_name_and_parent(
                visible_name, parent_uuid)
            entities_to_write.append(entity_uuid)

        return entities_to_write

    def _move_entity(self, entity_uuid: str, target_uuid: str) -> None:
        """
        Sets the parent of the provided entity to be the
        target UUID

        :param entity_uuid: entity which parent is updated
        :param target_uuid: the new parent of the entity
        """

        try:
            if self._entry_is_a_collection(entity_uuid) and \
                self._is_target_path_descendant_of_source_path(target_uuid, entity_uuid):
                raise ConstraintViolationError(
                    "collection can not be moved into itself or its descendant")

            if self._exists_visible_name_in_collection(entity_uuid, target_uuid):
                raise ConstraintViolationError(
                    f"destination must not contain a child with the same name: "
                    f"{self._repository.get_visible_name_for_uuid(entity_uuid)}")


            current_metadata: Metadata = self._repository.get_metadata_for_uuid(entity_uuid)
            new_metadata_entry: Metadata = copy.deepcopy(current_metadata)
            new_metadata_entry.parent = target_uuid

            self._repository.write_metadata(entity_uuid, new_metadata_entry)

        except (NotFoundError,
                InvalidMetadataError,
                ConstraintViolationError,
                RemarkableWriteError) as e:
            print(f"mv: {e} ")


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
            collection_pointer = self._repository.get_parent(collection_pointer)

        return False
