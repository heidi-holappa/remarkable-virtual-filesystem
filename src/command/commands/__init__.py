"""
Provides indirect access to commands for convenience.
A bit of controversial implementation approach, but
mentioned as one valid approach in PEP 0008, "Public
and internal interfaces"
"""

from src.command.commands.base_command import BaseCommand
from src.command.commands.rm import RemoveCommand
from src.command.commands.refresh import RefreshCommand
from src.command.commands.rcp import RemoteCopyCommand
from src.command.commands.mv import MoveCommand
from src.command.commands.mkdir import MakeDirectoryCommand
from src.command.commands.ls import ListCommand
from src.command.commands.help import HelpCommand
from src.command.commands.clear import ClearCommand
from src.command.commands.cd import ChangeDirectoryCommand
from src.command.commands.exit import ExitCommand
from src.command.commands.rename import RenameCommand

__all__ = [
    "BaseCommand",
    "RemoveCommand",
    "RefreshCommand",
    "RemoteCopyCommand",
    "MoveCommand",
    "MakeDirectoryCommand",
    "ListCommand",
    "HelpCommand",
    "ClearCommand",
    "ChangeDirectoryCommand",
    "ExitCommand",
    "RenameCommand",
]
