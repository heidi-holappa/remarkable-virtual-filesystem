import unittest
from io import StringIO
from unittest.mock import patch

from src.com.help import help_instruction


class TestHelpInstruction(unittest.TestCase):

    def test_help_method_prints_to_console(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction([])
            output: str = mock_out.getvalue()
            self.assertTrue("supported commands:" in output, msg=f"Output was: {output}")


    def test_help_with_command_as_arg(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction(["mv"])
            output: str = mock_out.getvalue()
            self.assertTrue("move entities to another collection" in output, msg=f"Output was: {output}")
            self.assertTrue("source or pattern" in output, msg=f"Output was: {output}")
            self.assertTrue("target-path" in output, msg=f"Output was: {output}")
            self.assertTrue("mv file.pdf /some/path" in output, msg=f"Output was: {output}")
            self.assertTrue("mv *.epub /some/path" in output, msg=f"Output was: {output}")
            self.assertTrue("mv * /some/path" in output, msg=f"Output was: {output}")

    def test_help_with_command__with_additional_info(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction(["mkdir"])
            output: str = mock_out.getvalue()
            self.assertTrue("make new directory" in output, msg=f"Output was: {output}")
            self.assertTrue("directory name" in output, msg=f"Output was: {output}")
            self.assertTrue("mkdir foo" in output, msg=f"Output was: {output}")
            self.assertTrue("additional information:" in output, msg=f"Output was: {output}")
            self.assertTrue("supported characters: a-zA-Z0-9._-" in output, msg=f"Output was: {output}")
            self.assertTrue("provided path must be a child of current path" in output, msg=f"Output was: {output}")


    def test_help_command_not_found(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction(["grep"])
            output: str = mock_out.getvalue()
            self.assertTrue("help: command not found: supported commands:" in output, msg=f"Output was: {output}")

    def test_help_with_invalid_number_of_args(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction(["one", "two"])
            output: str = mock_out.getvalue()
            self.assertTrue("help: usage: help or help <command>" in output, msg=f"Output was: {output}")


