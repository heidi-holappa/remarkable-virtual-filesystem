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

def cd(utility_arguments: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Handles command to change directory

    Usage examples:
      - cd foo
      - cd ../foo
      - cd /foo/bar

    :param utility_arguments: the path to which directory should be changed to
    :param workspace_manager: manager for reMarkable workspace
    """

    ws: RemarkableWorkspace = workspace_manager.get()

    if len(utility_arguments) == 0:
        ws.set_current_collection(ROOT_COLLECTION)
    elif len(utility_arguments) > 1:
        print("Usage: cd OR cd <path>")
        return
    else:
        try:
            operand: str = utility_arguments[0]
            ws.change_collection(operand)
        except (NoSuchFileOrDirectoryException,
                NotADirectoryException) as e:
            print(f"cd: {str(e)}")

def mv(utility_arguments: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of move command

    Usage examples:
      - mv a.pdf /foo
      - mv *.pdf ./bar

    :param utility_arguments: arguments given for the instruction
    :param workspace_manager: manager for reMarkable workspace
    """

    if len(utility_arguments) == 2:
        ws: RemarkableWorkspace = workspace_manager.get()
        operand_source, operand_target = utility_arguments
        ws.process_move_command(
            operand_source=operand_source, operand_target=operand_target)
    else:
        print("Usage (mvp): mv <filename without path> <path>")


def rm(utility_arguments: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of remove command.

    Usage examples:
      - rm file.pdf
      - rm /foo/bar
      - rm *.pdf

    :param utility_arguments: possible arguments
    :param workspace_manager: manager for reMarkable workspace
    """

    if len(utility_arguments) == 1:
        ws: RemarkableWorkspace = workspace_manager.get()
        operand = utility_arguments[0]
        ws.process_remove_command(target_pattern=operand)
    else:
        print("Usage: rm <file or path>")


def rcp(cmd_line: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Remote copy (rcp) copies either one PDF or EPUB file from host
    machine (user's computer running the python script) or all files
    in provided host directory to the target machine (reMarkable).

    Both source path and target collection must be provided with
    absolute paths, noting that the target path must be the absolute
    path in context of this application (i.e., the file structure
    shown in Xochitl GUI application), meaning that root path is '/',
    path to directory 'foo' whose parent is root is '/foo' or '/foo/'
    and so on.

    Usages:
      - rcp <source file> <target collection>
      - rcp -a <source_path> <target collection>

    :param cmd_line: source file and target collection
    :param workspace_manager: manager for reMarkable workspace
    """

    if len(cmd_line) == 2:
        ws: RemarkableWorkspace = workspace_manager.get()
        operand_source, operand_target = cmd_line
        ws.process_rcp_command_without_flags(
            source_file=operand_source,
            target_collection=operand_target)
    elif len(cmd_line) > 2:
        ws: RemarkableWorkspace = workspace_manager.get()
        ws.process_rcp_with_flags(cmd_line)
    else:
        print("rcp: usage: rcp <source file> <target collection>")


def ls(utility_arguments: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    A light implementation of the list command.

    Usage examples:
      - ls
      - ls <path>

    :param utility_arguments: arguments for the ls command
    :param workspace_manager: manager for reMarkable workspace
    """

    if len(utility_arguments) > 1:
        print("ls: usage: ls or ls <path or file>")
        return

    try:
        ws = workspace_manager.get()
        ws.process_ls(utility_arguments)
    except NotFoundException as e:
        print(e)

def mkdir(utility_arguments: List[str], workspace_manager: WorkspaceManager) -> None:
    """
    Tries to create a new directory

    :param utility_arguments: arguments provided for the mkdir command
    :param workspace_manager: manager for reMarkable workspace
    """
    if len(utility_arguments) != 1:
        print("mkdir: usage: mkdir <path>")
        return


    operand_path = utility_arguments[0]
    ws = workspace_manager.get()
    ws.process_mkdir(operand_path)

def clear() -> None:
    """
    Clears bash terminal

    Usage: clear
    """
    subprocess.run("clear", check=False)

def refresh(workspace_manager: WorkspaceManager) -> None:
    """
    Uses systemctl to restart xochitl

    :param workspace_manager: manager for reMarkable workspace
    """
    ws = workspace_manager.get()
    try:
        ws.restart_xochitl()
    except RemarkableOperationException as e:
        print(f"refresh: unexpected error occurred: {e}")


def handle_exit(workspace_manager: WorkspaceManager) -> None:
    """
    Exits the application

    :param workspace_manager: manager for reMarkable workspace
    """
    ws = workspace_manager.get()
    try:
        ws.restart_xochitl()
        sys.exit(0)
    except RemarkableOperationException as e:
        print(e)
        sys.exit(1)
