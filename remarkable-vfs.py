import shlex
import argparse
import logging
from argparse import ArgumentParser, Namespace
from typing import List

from src.com.common import clear, ls, mv, rm, cd, rcp, mkdir, rename, refresh, handle_exit
from src.com.help import help_instruction
from src.workspace.workspace_manager import default_workspace_manager as workspace_manager


def main_loop() -> None:

    ws = workspace_manager.get()

    while True:
        path = ws.get_current_path()
        cmd_line: List[str] = shlex.split(input(f"remarkable~{path}$ "))

        if not cmd_line:
            continue

        command, *utility_arguments = cmd_line

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
            case _:
                print(f"Command '{command}' not found.\nTry: help")


def init_argparse() -> ArgumentParser:
    """
    Initializes argument parser

    :return: initialized argument parser
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


def main() -> None:
    parser = init_argparse()
    init_logging(parser.parse_args())

    main_loop()