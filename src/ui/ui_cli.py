"""
Implementation for the CLI UI
"""
import shlex
import logging

from src.event.event import Event, OutputMessage, ProgressUpdate
from src.event.event_bus import EventBus
from src.command.command_dispatcher import CommandDispatcher
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.ui.ui_base import Ui


logger = logging.getLogger(__name__)

class CliUi(Ui):
    """
    Implementation for the CLI UI
    """

    def __init__(self, repository: RemarkableDataRepository, event_bus: EventBus,
                 dispatcher: CommandDispatcher) -> None:
        self._repository = repository
        self._dispatcher = dispatcher
        event_bus.subscribe(self.render_event)

    def loop(self) -> None:
        """
        Main loop reads inputs from user and attempts
        to resolve a command based on the input.
        """

        while True:
            path = self._repository.get_current_path()
            line = input(f"remarkable~{path}$ ")

            parsed = self._parse_command(line)

            if parsed is None:
                continue

            command, arguments = parsed

            self._dispatcher.dispatch(command, arguments)

    def render_event(self, event: Event) -> None:
        """
        Listens to events published by other application
        layers by subscribing to the event bus. Renders these
        messages to the terminal.
        """

        if isinstance(event, OutputMessage):
            print(
                f"{event.command}: "
                f"{event.message}")

        elif isinstance(event, ProgressUpdate):
            print(
                f"{event.command}: "
                f"{event.message}: "
                f"{event.current}/{event.total}"
            )

    @staticmethod
    def _parse_command(line: str) -> tuple[str, list[str]] | None:
        """
        Parses a command line into a command and its arguments.

        :param line: Raw command line entered by the user.
        :return: A tuple containing the command and its arguments, or None
            if the input is empty.
        """
        cmd_line = shlex.split(line)

        if not cmd_line:
            return None

        command, *arguments = cmd_line
        return command, arguments