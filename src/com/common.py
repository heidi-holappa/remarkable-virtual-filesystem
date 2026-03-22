"""
    A collection of common instructions used supported
    by reMarkable bash-emulator
"""

import subprocess
from typing import List

from src.constant import ROOT_COLLECTION
from src.exception.no_such_file_or_directory_exception import NoSuchFileOrDirectoryException
from src.exception.not_a_directory_exception import NotADirectoryException
from src.workspace.remarkable_workspace import RemarkableWorkspace
from src.workspace.workspace_manager import WorkspaceManager


def cd(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Handles command to change directory

    :param args: the path to which directory should be changed to
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """

    ws: RemarkableWorkspace = workspace_manager.get()

    if len(args) == 0:
        ws.set_current_collection(ROOT_COLLECTION)
    elif len(args) > 1:
        print("Usage: cd OR cd <path>")
        return
    else:
        try:
            ws.change_collection(args[0])
        except (NoSuchFileOrDirectoryException,
                NotADirectoryException) as e:
            print(f"cd: {str(e)}")

def mv(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of move command

    :param args: arguments given for the instruction
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """
    ws: RemarkableWorkspace = workspace_manager.get()

    if len(args) == 2:
        ws.process_move_command(*args)
    else:
        print("Usage (mvp): mv <filename without path> <path>")


def rm(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of remove command.

    :param args: possible arguments
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """
    ws: RemarkableWorkspace = workspace_manager.get()

    if len(args) == 1:
        ws.process_remove_command(args[0])
    else:
        print("Usage: rm <file or path>")


def ls(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of the list command.

    :param args: arguments for the ls command
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """
    ws = workspace_manager.get()

    remarkable_metadata = ws.get_data()

    if args:
        print("ls: usage: ls")
        return

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
