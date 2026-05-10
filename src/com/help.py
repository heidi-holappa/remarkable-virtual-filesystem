"""
    Method for help instruction
"""
from typing import Dict, List
SUPPORTED_INSTRUCTIONS: Dict[str, Dict[str, str | List[str]]] = {


  "clear": {
      "description": "clears screen",
      "usage": [
          "clear"
      ],
      "args": []
  },
  "ls": {
      "description": "clears screen",
      "args": [
          "path\tan absolute or relative path from which to list files"
      ],
      "usage": [
          "ls",
          "ls /some/path"
      ],
  },
  "mv": {
      "description": "move entities to another collection",
      "args": [
          "source\ta specific entity to move or a pattern with '*' wildcard",
          "target\tabsolute or relative path to which to move entities"],
      "usage": [
          "mv file.pdf /some/path",
          "mv *.epub /some/path",
          "mv * /some/path"],
  },
  "rm": {
      "description": "remove entities",
      "args": [
          "source\ta specific entity to remove or a pattern with '*' wildcard"
      ],
      "usage": [
          "rm file.pdf",
          "rm path/","rm *.pdf",
          "rm *"
      ],
  },
  "mkdir": {
      "description": "make new directory",
      "args": [
          "directory\tname of the directory to create",
      ],
      "usage": [
          "mkdir foo"
      ],
      "info": ["supported characters: a-zA-Z0-9._-",
               "provided path must be a child of current path"]
  },
  "rcp": {
      "description": "remote copy one PDF or EPUB file from host-machine to reMarkable",
      "args": [
          "-a\tflag to copy all files in source path. When using this flag, the source must be a path",
          "source\tabsolute path for source (file) to copy or a path, if flag -a is used",
          "target\tabsolute path to target directory"
      ],
      "usage": [
          "rcp /path/to/host/machine/file.pdf /path/on/remarkable",
          "rcp -a /path/on/host/ /path/on/remarkable"
      ],
  },
  "refresh": {
      "description": "restarts xochitl GUI application",
      "args": [],
      "usage": ["refresh"],
  },
  "help": {
      "description": "show help texts",
      "args": [
          "command\tcommand for which help text should be shown"
      ],
      "usage": [
          "help",
          "help mkdir"
      ],
  },
  "exit": {
      "description": "exits program and restarts xochitl",
      "args": [],
      "usage": [
          "exit",
          "x"
      ],
  },
}


def help_instruction(args: List[str]):
    """
        Help message provides instructions on how to
        use the reMarkable bash-emulator

        :param args: a list of args provided by the user
    """

    if len(args) > 1:
        print("help: usage: help or help <command>")
        return

    if args:
        command = args[0]
        if not SUPPORTED_INSTRUCTIONS.get(command):
            print("help: command not found: supported commands:")
            list_commands()
        else:
            print_command_details(command)
    else:
        print_command_details("help")
        print("")
        list_commands()

def print_command_details(command: str) -> None:
    """
    A helper to print out instructions for a given command

    :param command: a command to print out
    """

    print("")
    command_help = SUPPORTED_INSTRUCTIONS.get(command)
    print(f"{command}: {command_help.get("description")}")
    if command_help.get("args"):
        print("")
        print("  args:")
        for arg in command_help.get("args"):
            print(f"    {arg}")
    if command_help.get("usage"):
        print("")
        print("  usage:")
        for usage in command_help.get("usage"):
            print(f"    {usage}")
    if command_help.get("info"):
        print("")
        print("  additional information:")
        for info in command_help.get("info"):
            print(f"    {info}")
    print("")


def list_commands() -> None:
    """
    Lists commands from dictionary
    """
    print("supported commands:")
    for com in SUPPORTED_INSTRUCTIONS:
        print(f"  {com}")
