import subprocess
from src.command.commands.base_command import BaseCommand


class ClearCommand(BaseCommand):
    """
    TODO
    """

    def handle(self, args: list[str]) -> None:
        """
        Clears bash terminal

        Usage: clear
        """
        subprocess.run("clear", check=False)