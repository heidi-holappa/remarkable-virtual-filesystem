"""
    A collection of common instructions used supported
    by reMarkable bash-emulator
"""

import subprocess
from typing import List

from src.constant import ROOT_COLLECTION
from src.workspace.workspace_manager import WorkspaceManager


def cd(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Instruction for change directory command

    :param args: the path to which directory should be changed to
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """

    ws = workspace_manager.get()

    if len(args) == 0:
        ws.set_current_collection(ROOT_COLLECTION)
    elif len(args) > 1:
        print("Usage: cd OR cd <path>")
        return
    else:
        ws.change_collection(args[0])

def mv(args: List[str]) -> None:
    """
    A light implementation of move command

    TODO: implement mv

    :param args: arguments given for the instruction
    :return: None
    """
    print(f"Move not implemented. Called with args: {args}")


def rm(args: List[str]) -> None:
    """
    A light implementation of remove command.

    TODO: implement rm

    :param args: possible arguments
    :return: None
    """
    print(f"Remove not implemented. Called with args: {args}")

def ls(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of the list command.

    TODO: add support for args

    :param args: arguments for the ls command
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """
    ws = workspace_manager.get()

    remarkable_metadata = ws.get_data()

    print(f"List called with args: {args}")

    result = []
    for uuid, v in remarkable_metadata.items():
        if v.get('parent') != ws.get_current_collection():
            continue
        path_and_file = ws.generate_absolute_collection_path(uuid)
        if v.get('size'):
            path_and_file = str(v.get('size')) + '\t' + path_and_file
        result.append(path_and_file)

    for e in sorted(result):
        print(e)

def clear() -> None:
    """
        Clears bash terminal
    :return: None
    """
    subprocess.run("clear", check=False)
