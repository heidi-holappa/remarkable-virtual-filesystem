"""Entry point and command loop for the Remarkable Virtual File System."""

import shlex
import argparse
import logging
from argparse import ArgumentParser, Namespace
from typing import List

from src.com.common import clear, ls, mv, rm, cd, rcp, mkdir, rename, refresh, handle_exit
from src.com.help import help_instruction
from src.workspace.workspace_manager import default_workspace_manager as workspace_manager

logger = logging.getLogger(__name__)

def main_loop() -> None:
    """
    Runs the interactive command loop.

    Reads commands from standard input, parses them, and executes them
    until the user issues an exit command.
    """
    ws = workspace_manager.get()

    while True:
        path = ws.get_current_path()
        line = input(f"remarkable~{path}$ ")

        parsed = parse_command(line)

        if parsed is None:
            continue

        command, arguments = parsed

        if not execute_command(command, arguments):
            return

def parse_command(line: str) -> tuple[str, list[str]] | None:
    """
    Parses a command line into a command and its arguments.

    :param line: Raw command line entered by the user.
    :return: A tuple containing the command and its arguments, or None
        if the input is empty.
    """
    cmd_line = shlex.split(line)

    if not cmd_line:
        return None

    command, *arguments = cmd_line
    return command, arguments

def execute_command(
    command: str,
    utility_arguments: List[str],
) -> bool:
    """
    Executes a command with the supplied arguments.

    :param command: Command name to execute.
    :param utility_arguments: Arguments passed to the command.
    :return: True if the command loop should continue, False if it
        should terminate.
    """
    match command:
        case "cd":
            cd(utility_arguments, workspace_manager)
        case "clear":
            clear()
        case "rm":
            rm(utility_arguments, workspace_manager)
        case "ls":
            ls(utility_arguments, workspace_manager)
        case "mv":
            mv(utility_arguments, workspace_manager)
        case "rcp":
            rcp(utility_arguments, workspace_manager)
        case "help":
            help_instruction(utility_arguments)
        case "refresh":
            refresh(workspace_manager)
        case "mkdir":
            mkdir(utility_arguments, workspace_manager)
        case "rename":
            rename(utility_arguments, workspace_manager)
        case "exit" | "x":
            handle_exit(workspace_manager)
            return False
        case _:
            print(f"Command '{command}' not found.\nTry: help")

    return True

def init_argparse() -> ArgumentParser:
    """
    Creates and configures the command-line argument parser.

    :return: Configured argument parser.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--log", action="store_true")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARN", "ERROR"],
        default="INFO",
    )
    return parser


def init_logging(args: Namespace) -> None:
    """
    Configures application logging when logging is enabled.

    :param args: Parsed command-line arguments containing logging options.
    """
    if args.log:
        level = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "ERROR": logging.ERROR,
        }[args.log_level]

        logging.basicConfig(
            level=level,
            format="%(levelname)s:%(name)s: %(message)s",
        )
        logger.info("Logging enabled. Using log level %s" , args.log_level)


def main() -> None:
    """
    Initializes the application and starts the main command loop.
    """
    parser = init_argparse()
    args = parser.parse_args()
    init_logging(args)

    logger.info("Starting Remarkable VirtualFilesSystem main loop")

    main_loop()


if __name__ == "__main__":
    main()
