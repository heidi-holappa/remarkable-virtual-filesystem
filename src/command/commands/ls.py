"""
Implementation of list command
"""
from src.constant import (
    ROOT_COLLECTION,
    LS_COLUMN_WIDTH)

from src.exception import NotFoundError

from src.dto.entry import Entry
from src.dto.entry_type_enum import EntityType
from src.event.event import OutputCommandMessage, OutputMessage
from .base_command import BaseCommand

# pylint: disable=too-few-public-methods
class ListCommand(BaseCommand):
    """
    Implementation of list command
    """

    def handle(self, args: list[str]) -> None:
        """
        A light implementation of the list command.

        Usage examples:
          - ls
          - ls <path>

        :param args: arguments for the ls command
        """

        if len(args) > 1:
            self._event_bus.publish(
                OutputCommandMessage(
                    "ls",
                    "usage: ls or ls <path or file>"
                )
            )
            return

        try:
            self._process_ls(args)
        except NotFoundError as e:
            self._event_bus.publish(
                OutputCommandMessage(
                    "ls",
                    f"{e}"
                )
            )

    def _process_ls(self, args: list[str]) -> None:
        """
        Processes ls command and lists files either in current
        collection or matching the provided argument. The argument
        is expected to be a path (collection). If argument is provided,
        and it does not match any collection, raises NotFoundError.

        :param args: optional utility arguments for ls
        """
        collection_to_list_uuid = self._get_collection_to_list_uuid(args)
        list_result = self._generate_list_output(collection_to_list_uuid)
        self._output_ls_result(list_result)

    def _get_collection_to_list_uuid(self, args: list[str]) -> str:
        """
        Resolves the UUID for the collection whose
        content is to be listed.

        Raises:
            NotFoundError if collection is not found

        :param args: possible path as an argument
        """
        if args:
            operand_path: str = args[0]
            collection_to_list_uuid: str | None = (
                self._traverse_path(operand_path))
            if collection_to_list_uuid is None:
                raise NotFoundError("no such path")
            return collection_to_list_uuid

        return self._repository.get_current_collection()


    def _generate_list_output(self, collection_to_list_uuid: str) -> list[str]:
        """
        Collects the items in the provided collection
        and generates the list command output

        :param collection_to_list_uuid: uuid of the collection
        """

        remarkable_metadata: dict[str, Entry] = self._repository.get_data()

        list_result: list[str] = []
        collections: list[tuple[str, str]] = []
        documents: list[tuple[str, str]] = []

        if collection_to_list_uuid != ROOT_COLLECTION:
            list_result.append(f"{' ' * LS_COLUMN_WIDTH}../")
        list_result.append(f"{' ' * LS_COLUMN_WIDTH}./")

        for entry in remarkable_metadata.values():
            if entry.metadata.parent != collection_to_list_uuid:
                continue
            size: int = 0
            if entry.size:
                size = entry.size
            if entry.metadata.type == EntityType.COLLECTION_TYPE:
                collection_visible_name: str = entry.metadata.visible_name
                collections.append((f"{collection_visible_name}/", f"{size}"))
            elif entry.metadata.type == EntityType.DOCUMENT_TYPE:
                document_visible_name: str = entry.metadata.visible_name
                documents.append((f"{document_visible_name}", f"{size}"))
        for t in sorted(collections, key=lambda x: x[0].lower()):
            name, entry_size = t
            padding_col: str = ' ' * (LS_COLUMN_WIDTH - len(entry_size))
            list_result.append(f"{entry_size}{padding_col}{name}")

        for t in sorted(documents, key=lambda x: x[0].lower()):
            name, entry_size = t
            padding_doc: str = ' ' * (LS_COLUMN_WIDTH - len(entry_size))
            list_result.append(f"{entry_size}{padding_doc}{name}")

        return list_result


    def _output_ls_result(self, list_result: list[str]) -> None:
        size_header = "size (kB)"
        header_padding = " " * (LS_COLUMN_WIDTH - len(size_header))
        name_header = "name"
        header = f"{size_header}{header_padding}{name_header}"
        self._event_bus.publish(OutputMessage(f"{header}"))
        for entry in list_result:
            self._event_bus.publish(OutputMessage(f"{entry}"))
