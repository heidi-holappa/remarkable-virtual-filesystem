from collections.abc import Callable

from commands import (
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
    ExitCommand
)

from src.exception import (
    InvalidArgumentError
)


class CommandDispatcher:
    """
    Dispatches commands to their respective handlers.

    Command instances are initialized lazily and cached per dispatcher.
    """

    _factories: dict[str, Callable[[], BaseCommand]] = {
        "rm": RemoveCommand,
        "refresh": RefreshCommand,
        "rcp": RemoteCopyCommand,
        "mv": MoveCommand,
        "mkdir": MakeDirectoryCommand,
        "ls": ListCommand,
        "help": HelpCommand,
        "clear": ClearCommand,
        "cd": ChangeDirectoryCommand,
        "exit": ExitCommand
    }

    _aliases: dict[str, tuple[str, list[str]]] = {
        "x": ("exit", [])
    }


    def __init__(self) -> None:
        self._instances: dict[str, BaseCommand] = {}



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
            instance = factory()
            self._instances[command] = instance

        instance.handle(args)
