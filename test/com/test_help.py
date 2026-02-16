import unittest
from io import StringIO
from unittest.mock import patch
from src.com.help import help_instruction


class TestHelpInstruction(unittest.TestCase):

    def test_help_method_prints_to_console(self) -> None:
        with patch('sys.stdout', new=StringIO()) as mock_out:
            help_instruction()
            output: str = mock_out.getvalue()
            self.assertTrue("Supported commands:" in output, msg=f"Output was: {output}")


