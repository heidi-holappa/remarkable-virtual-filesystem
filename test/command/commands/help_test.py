import copy
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
from src.repository.remarkable_data_repository import RemarkableDataRepository
from src.data.remarkable_ssh_metadata_source_v2 import RemarkableSSHMetadataSourceV2
from src.command.commands.help import HelpCommand

from test.test_data_v2 import (
    TEST_DATA)


class TestHelpInstruction(unittest.TestCase):

    @patch.object(RemarkableSSHMetadataSourceV2, "load")
    def setUp(self, mock_load: MagicMock) -> None:
        mock_load.return_value = copy.deepcopy(TEST_DATA)
        self._help = HelpCommand(
            RemarkableDataRepository(RemarkableSSHMetadataSourceV2()))

    def test_help_method_prints_to_console(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self._help.handle([])
            output: str = mock_out.getvalue()
            self.assertTrue("supported commands:" in output, msg=f"Output was: {output}")


    def test_help_with_command_as_arg(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self._help.handle(["mv"])
            output: str = mock_out.getvalue()
            self.assertTrue("move entities to another collection" in output, msg=f"Output was: {output}")
            self.assertTrue("source" in output, msg=f"Output was: {output}")
            self.assertTrue("target" in output, msg=f"Output was: {output}")
            self.assertTrue("mv file.pdf /some/path" in output, msg=f"Output was: {output}")
            self.assertTrue("mv *.epub /some/path" in output, msg=f"Output was: {output}")
            self.assertTrue("mv * /some/path" in output, msg=f"Output was: {output}")

    def test_help_with_command__with_additional_info(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self._help.handle(["mkdir"])
            output: str = mock_out.getvalue()
            self.assertTrue("make new directory" in output, msg=f"Output was: {output}")
            self.assertTrue("directory" in output, msg=f"Output was: {output}")
            self.assertTrue("mkdir foo" in output, msg=f"Output was: {output}")
            self.assertTrue("additional information:" in output, msg=f"Output was: {output}")
            self.assertTrue("supported characters: a-zA-Z0-9._-" in output, msg=f"Output was: {output}")
            self.assertTrue("provided path must be a child of current path" in output, msg=f"Output was: {output}")


    def test_help_command_not_found(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self._help.handle(["grep"])
            output: str = mock_out.getvalue()
            self.assertTrue("help: command not found: supported commands:" in output, msg=f"Output was: {output}")

    def test_help_with_invalid_number_of_args(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            self._help.handle(["one", "two"])
            output: str = mock_out.getvalue()
            self.assertTrue("help: usage: help or help <command>" in output, msg=f"Output was: {output}")


