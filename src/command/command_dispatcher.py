from collections.abc import Callable

from src.command.commands import (
    BaseCommand,
    RemoveCommand,
    RefreshCommand,
    RemoteCopyCommand,
    MoveCommand,
    MakeDirectoryCommand,
    ListCommand,
    HelpCommand,
    ClearCommand,
    ChangeDirectoryCommand,
    ExitCommand,
    RenameCommand
)
from src.repository.remarkable_data_repository import RemarkableDataRepository

from src.exception import (
    InvalidArgumentError
)


class CommandDispatcher:
    """
    Dispatches commands to their respective handlers.

    Command instances are initialized lazily and cached per dispatcher.
    """


    def __init__(self, repository: RemarkableDataRepository) -> None:
        self._instances: dict[str, BaseCommand] = {}
        self._repository = repository

        self._factories: dict[str, Callable[[], BaseCommand]] = { # type: ignore
            "rm": RemoveCommand,
            "refresh": RefreshCommand,
            "rcp": RemoteCopyCommand,
            "mv": MoveCommand,
            "mkdir": MakeDirectoryCommand,
            "ls": ListCommand,
            "help": HelpCommand,
            "clear": ClearCommand,
            "cd": ChangeDirectoryCommand,
            "exit": ExitCommand,
            "rename": RenameCommand
        }

        self._aliases: dict[str, tuple[str, list[str]]] = {
            "x": ("exit", [])
        }


    def dispatch(self, command: str, args: list[str]) -> None:
        """
        Resolve and execute a command.

        Raises:
            InvalidArgumentError: If the command is not registered.

        :param command: Command name or alias.
        :param args: Arguments passed to the command.
        """

        if command in self._aliases:
            command, alias_args = self._aliases[command]
            args = [*alias_args, *args]


        factory = self._factories.get(command)

        if factory is None:
            raise InvalidArgumentError(f"{command}: command not found")


        instance = self._instances.get(command)

        if instance is None:
            instance = factory(self._repository)
            self._instances[command] = instance

        instance.handle(args)
