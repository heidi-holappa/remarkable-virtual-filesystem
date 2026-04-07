"""
    A collection of common instructions used supported
    by reMarkable bash-emulator
"""

import sys
import subprocess
from typing import List

from src.constant import ROOT_COLLECTION
from src.exception.no_such_file_or_directory_exception import NoSuchFileOrDirectoryException
from src.exception.not_a_directory_exception import NotADirectoryException
from src.exception.not_found_exception import NotFoundException
from src.exception.remarkable_operation_exception import RemarkableOperationException
from src.workspace.remarkable_workspace import RemarkableWorkspace
from src.workspace.workspace_manager import WorkspaceManager

def cd(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Handles command to change directory

    Usage examples:
      - cd foo
      - cd ../foo
      - cd /foo/bar

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

    Usage examples:
      - mv a.pdf /foo
      - mv *.pdf ./bar

    :param args: arguments given for the instruction
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """

    if len(args) == 2:
        ws: RemarkableWorkspace = workspace_manager.get()
        ws.process_move_command(*args)
    else:
        print("Usage (mvp): mv <filename without path> <path>")


def rm(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of remove command.

    Usage examples:
      - rm file.pdf
      - rm /foo/bar
      - rm *.pdf

    :param args: possible arguments
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """

    if len(args) == 1:
        ws: RemarkableWorkspace = workspace_manager.get()
        ws.process_remove_command(args[0])
    else:
        print("Usage: rm <file or path>")


def rcp(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Remote copy (rcp) copies one PDF or EPUB file from host machine
    (user's computer running the python script) to the target machine
    (reMarkable). Both source path and target collection must be
    provided with absolute paths, noting that the target path must
    be the absolute path in context of this application (i.e., the
    file structure shown in Xoctihl GUI application), meaning that
    root path is '/', path to directory 'foo' whose parent is root
    is '/foo' or '/foo/' and so on.

    Usage: rcp <source file> <target collection>

    :param args: source file and target collection
    :param workspace_manager: manager for reMarkable workspace
    :return:
    """

    if len(args) == 2:
        ws: RemarkableWorkspace = workspace_manager.get()
        source_file, target_path = args
        ws.process_rcp_command(source_file, target_path)

    else:
        print("rcp: usage: rcp <source file> <target collection>")


def ls(args: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of the list command.

    Usage examples:
      - ls
      - ls <path>

    :param args: arguments for the ls command
    :param workspace_manager: manager for reMarkable workspace
    :return: None
    """

    if len(args) > 1:
        print("ls: usage: ls or ls <path or file>")
        return

    try:
        ws = workspace_manager.get()
        ws.process_ls(args)
    except NotFoundException as e:
        print(e)

def clear() -> None:
    """
    Clears bash terminal

    Usage: clear

    :return: None
    """
    subprocess.run("clear", check=False)

def refresh(workspace_manager: WorkspaceManager) -> None:
    """
    Uses systemctl to restart xochitl

    :return: None
    """
    ws = workspace_manager.get()
    try:
        ws.restart_xochitl()
    except RemarkableOperationException as e:
        print(f"refresh: unexpected error occurred: {e}")


def handle_exit(workspace_manager: WorkspaceManager) -> None:
    """
    Exits the application

    :return: None
    """
    ws = workspace_manager.get()
    try:
        ws.restart_xochitl()
        sys.exit(0)
    except RemarkableOperationException as e:
        print(e)
        sys.exit(1)
