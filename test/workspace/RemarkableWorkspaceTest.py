import unittest
from typing import Dict

from src.workspace.RemarkableWorkspace import RemarkableWorkspace
from src.exception.NotFoundException import NotFoundException
from src.exception.InvalidPathException import InvalidPathException
from src.constant import COLLECTION_NOT_FOUND, INVALID_PATH

class RemarkableWorkspaceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.TEST_DATA: Dict[str, Dict[str, str]] = {
            "": {"type": "CollectionType", "parent": "", "visibleName": ""},
            "a": {"type": "CollectionType", "parent": "", "visibleName": "A"},
            "a_0": {"type": "CollectionType", "parent": "a", "visibleName": "A_0"},
            "b": {"type": "CollectionType", "parent": "", "visibleName": "B"},
            "b_0": {"type": "CollectionType", "parent": "b", "visibleName": "B_0"},
        }
        self.ws = RemarkableWorkspace(self.TEST_DATA)

    # Get parent
    def test_get_parent_returns_correct_parent_when_parent_is_other_than_root(self) -> None:
        assert self.ws.get_parent("b_0") == "b"

    def test_get_parent_return_correct_parent_when_parent_is_root(self) -> None:
        assert self.ws.get_parent("a") == ""

    def test_get_parent_handles_root_correctly(self) -> None:
        # per requirements root should return empty string
        assert self.ws.get_parent("") == ""

    def test_get_parent_for_collection_not_found_is_handled_gracefully(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            self.ws.get_parent("C")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    ## Get collection
    def test_get_collection_when_current_collection_is_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A", "") == "a"

    def test_get_collection_when_current_collection_is_not_root_and_collection_is_found(self) -> None:
        assert self.ws.get_collection("A_0", "a") == "a_0"

    def test_get_collection_when_current_collection_is_root_and_collection_is_not_found(self) -> None:
        assert self.ws.get_collection("C", "") == None

    # Set current collection
    def test_set_current_collection_with_valid_collection(self) -> None:
        self.ws.set_current_collection('a')
        assert self.ws.get_current_collection() == 'a'

    def test_set_current_collection_with_invalid_collection(self) -> None:
        with self.assertRaises(NotFoundException) as context:
            self.ws.set_current_collection("c")

        self.assertTrue(COLLECTION_NOT_FOUND in str(context.exception))

    ## Change collection/directory tests
    def test_change_collection_from_root_to_direct_subpath(self) -> None:

        self.ws.change_collection("/A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_from_root_to_direct_subpath_with_additional_slashes(self) -> None:
        self.ws.change_collection("//////////A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_from_root_to_direct_subpath_with_relative_directories(self) -> None:
        self.ws.change_collection("/././../A/..////A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_to_nested_subpath_with_absolute_path(self) -> None:
        self.ws.change_collection("/A/A_0")
        assert self.ws.get_current_collection() == "a_0"

    def test_change_collection_to_nested_subpath_with_relative_path(self)  -> None:
        # assumming the collection is A before the path change
        self.ws.change_collection("/A")
        self.ws.change_collection("../B/B_0")
        # then the new path should be /B/B_0
        assert self.ws.get_current_collection() == "b_0"

    def test_change_collection_with_invalid_path_raises_error(self) -> None:
        with self.assertRaises(InvalidPathException) as context:
            self.ws.change_collection("C")

        self.assertTrue(INVALID_PATH in str(context.exception))

    # Get absolute path
    def test_root_path_is_output_correctly(self) -> None:
        self.assertEqual("/", self.ws.generate_absolute_collection_path(""))

    def test_direct_subdirectory_to_root_output_correctly(self) -> None:
        self.assertEqual("/A", self.ws.generate_absolute_collection_path("a"))

    def test_nested_subdirectory_output_correctly(self) -> None:
        self.assertEqual("/A/A_0", self.ws.generate_absolute_collection_path("a_0"))