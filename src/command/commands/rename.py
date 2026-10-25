import copy

from .base_command import BaseCommand

from src.dto.metadata import Metadata
from src.constant import VALID_VISIBLE_NAME_REGEX

from src.exception import (
    InvalidArgumentError,
    NotFoundError
)

class RenameCommand(BaseCommand):
    """
    TODO
    """

    def handle(self, args: list[str]) -> None:
        """
        Tries to rename a file

        :param args: arguments provided for the rename command
        """
        if len(args) != 2:
            print("rename: usage: rename <file or path> <new name>")
            return
        operand_target, new_visible_name = args

        self.process_rename(operand_target, new_visible_name)

    def process_rename(self, target: str, new_visible_name: str) -> None:
        """
        Tries to rename a document or a collection with
        the provided new_visible_name. User is informed,
        if the new_visible_name violates naming constraints
        or if target does not exist.

        :param target: target entry to rename
        :param new_visible_name: new name for the source
        """
        try:

            visible_name, parent_uuid =  self._resolve_source_parent_and_visible_name(target)

            entity_uuid: str = self._get_uuid_with_visible_name_and_parent(
                visible_name, parent_uuid)

            self._validate_visible_name(parent_uuid, entity_uuid, new_visible_name)

            current_metadata = self._repository.get_metadata_for_uuid(entity_uuid)
            updated_metadata: Metadata = copy.deepcopy(current_metadata)
            updated_metadata.visible_name = new_visible_name

            # update metadata to in-memory data and target machine
            self._repository.write_metadata(entity_uuid, updated_metadata)

        except InvalidArgumentError as e:
            print(f"rename: {target} {new_visible_name}: {e}: hint: help rename")
        except NotFoundError as e:
            print(f"rename: {target} {new_visible_name}: {e}: hint: help rename")


    def _validate_visible_name(self, parent_uuid: str,
                               entry_uuid: str,
                               new_visible_name :str) -> None:
        """
        Validates that the provided visible name
        fills the following constraints:

        * visible name can contain alphanumeric characters
          (a-zA-Z0-9), slash (-), underscore (_) and dots (.)
        * visible name can not be None or an empty string
        * parent must not have child entry with same name

        :param parent_uuid: parent of the entry to be renamed
        :param entity_uuid: uuid of entry to rename
        :param new_visible_name: visible name of an entry

        raises:
          * invalid argument exception: if visible name
            fails validation
        """

        if not new_visible_name:
            raise InvalidArgumentError("visible name cannot be an empty string")
        if self._has_visible_name_equal_to_entry_uuid_in_collection(
                entry_uuid, new_visible_name, parent_uuid):
            raise InvalidArgumentError("parent has a child with the same name")
        if not bool(VALID_VISIBLE_NAME_REGEX.fullmatch(new_visible_name)):
            raise InvalidArgumentError("visible name contains invalid characters")