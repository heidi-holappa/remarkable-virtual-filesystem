"""Entry point and command loop for the Remarkable Virtual File System."""

import argparse
import logging
from argparse import ArgumentParser, Namespace

from src.command.command_dispatcher import CommandDispatcher
from src.ui.ui_cli import CliUi
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.event.event_bus import EventBus

from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2


logger = logging.getLogger(__name__)

def main_loop() -> None:
    """
    Runs the interactive command loop.

    Reads commands from standard input, parses them, and executes them
    until the user issues an exit command.
    """

    repository = RemarkableDataRepository(RemarkableSSHMetadataSourceV2())
    event_bus = EventBus()
    dispatcher = CommandDispatcher(repository, event_bus)
    ui = CliUi(repository, event_bus, dispatcher)

    logger.info("Starting UI")
    ui.loop()


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


if __name__ == "__main__": # pragma: no cover
    main()
