"""
    Method for help instruction
"""
from typing import Dict, List
SUPPORTED_INSTRUCTIONS: Dict[str, Dict[str, str | List[str]]] = {


  "clear": {
      "description": "clears screen",
      "usage": ["clear"],
      "args": []
  },
  "ls": {
      "description": "clears screen",
      "args": ["path"],
      "usage": ["ls", "ls /some/path"],
  },
  "mv": {
      "description": "move entities to another collection",
      "args": ["source or pattern", "target-path"],
      "usage": [
          "mv file.pdf /some/path",
          "mv *.epub /some/path",
          "mv * /some/path"],
  },
  "rm": {
      "description": "remove entities",
      "args": ["source or pattern"],
      "usage": ["rm file.pdf", "rm path/","rm *.pdf", "rm *"],
  },
  "mkdir": {
      "description": "make new directory",
      "args": ["directory name"],
      "usage": ["mkdir foo"],
      "info": ["supported characters: a-zA-Z0-9._-",
               "provided path must be a child of current path"]
  },
  "rcp": {
      "description": "remote copy one PDF or EPUB file from host-machine to reMarkable",
      "args": ["source (absolute)", "target-path (absolute)"],
      "usage": ["rcp /path/to/host/machine/file.pdf /path/on/remarkable"],
  },
  "refresh": {
      "description": "restarts xochitl GUI application",
      "args": [],
      "usage": ["refresh"],
  },
  "help": {
      "description": "show help texts",
      "args": ["command"],
      "usage": ["help", "help command"],
  },
  "exit": {
      "description": "exits program and restarts xochitl",
      "args": [],
      "usage": ["exit", "x"],
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
