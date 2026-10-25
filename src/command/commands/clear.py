"""
Implementation of clear command
"""

import subprocess
from src.command.commands.base_command import BaseCommand

# pylint: disable=too-few-public-methods
class ClearCommand(BaseCommand):
    """
    Clear command clears the user terminal view.
    """

    def handle(self, args: list[str]) -> None:
        """
        Clears bash terminal

        Usage: clear

        :param args: a list of arguments (empty for clear)
        """
        subprocess.run("clear", check=False)
