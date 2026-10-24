import copy
import os
import unittest
from io import StringIO
from typing import List, Set
from unittest.mock import patch, MagicMock

from src.constant import PARENT_NOT_FOUND, NO_SUCH_FILE_OR_DIRECTORY
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.exception import (
    NotFoundError,
    NoSuchFileOrDirectoryError,
    NoSuchDirectoryError,
    RemarkableWriteError,
    InvalidPathError
)
from src.workspace.remarkable_workspace_v2 import RemarkableWorkspaceV2
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.command.commands.base_command import BaseCommand
from test.test_data_v2 import (
    TEST_DATA,
    UUID_ROOT,
    UUID_A, UUID_A0, UUID_A1,
    UUID_B, UUID_B0, UUID_A_UNDER_B, UUID_C,
    UUID_FAIRYTALE, UUID_FAIRYTALE_2,
    UUID_A0_UNDER_B, UUID_D_1, UUID_FAIRYTALE_COPY)


class BaseCommandTest(unittest.TestCase):


    def setUp(self) -> None:
        pass