"""
Implementation of the remove command
"""
from src.exception import NotFoundError
from .base_command import BaseCommand

class RemoveCommand(BaseCommand):
    """
    Implementation of the remove command
    """

    def handle(self, args: list[str]) -> None:
        """
        A light implementation of remove command.

        Usage examples:
          - rm file.pdf
          - rm /foo/bar
          - rm *.pdf

        :param args: possible arguments
        """

        if len(args) == 1:
            operand = args[0]
            self.process_remove_command(target_pattern=operand)
        else:
            print("Usage: rm <file or path>")



    def process_remove_command(self, target_pattern: str) -> None:
        """
        A remove command removes one or several entities
        (documents and/or collections) matching the provided
        pattern from the reMarkable device.

        Handles following exceptions and informs user of an error:
          - NotFoundError if source path is not found
          - KeyError: if UUID is not found for data to be removed

        :param target_pattern: pattern for sources to be removed
        """

        try:
            visible_name, parent_uuid = self._resolve_source_parent_and_visible_name(target_pattern)

            entities_to_remove: list[str] = (
                self._collect_uuids_matching_name_or_pattern_and_all_descendants_of_matches(
                visible_name, parent_uuid))

            self._repository.remove_entities(entities_to_remove)

            for item_uuid in entities_to_remove:
                self._repository.remove_entry(item_uuid)

        except (NotFoundError, KeyError) as e:
            print(f"ERROR: {e}")
