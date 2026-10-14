"""
Provides indirect access to commands for convenience.
A bit of controversial implementation approach, but
mentioned as one valid approach in PEP 0008, "Public
and internal interfaces"
"""

from .base_command import BaseCommand
from .cd import ChangeDirectoryCommand
from .clear import ClearCommand
from .help import HelpCommand
from .ls import ListCommand
from .mkdir import MakeDirectoryCommand
from .mv import MoveCommand
from .rcp import RemoteCopyCommand
from .refresh import RefreshCommand
from .rm import RemoveCommand
from .exit import ExitCommand
