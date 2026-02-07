import unittest
from typing import Dict

from src.workspace.RemarkableWorkspace import RemarkableWorkspace

class RemarkableWorkspaceTest(unittest.TestCase):

    def setUp(self) -> None:
        self.TEST_DATA: Dict[str, Dict[str, str]] = {
            "root": {"type": "CollectionType", "parent": "", "visibleName": ""},
            "a": {"type": "CollectionType", "parent": "", "visibleName": "A"},
            "a_0": {"type": "CollectionType", "parent": "a", "visibleName": "A_0"},
            "b": {"type": "CollectionType", "parent": "", "visibleName": "B"},
            "b_0": {"type": "CollectionType", "parent": "b", "visibleName": "B_0"},
        }
        self.ws = RemarkableWorkspace(self.TEST_DATA)

    def test_change_collection_from_root_to_direct_subpath(self):

        self.ws.change_collection("/A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_from_root_to_direct_subpath_with_additional_slashes(self):
        self.ws.change_collection("//////////A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_from_root_to_direct_subpath_with_relative_directories(self):
        self.ws.change_collection("/././../A/..////A")
        assert self.ws.get_current_collection() == "a"

    def test_change_collection_to_nested_subpath_with_absolute_path(self):
        self.ws.change_collection("/A/A_0")
        assert self.ws.get_current_collection() == "a_0"

    def test_change_collection_to_nested_subpath_with_relative_path(self):
        # assumming the collection is A before the path change
        self.ws.change_collection("/A")
        self.ws.change_collection("../B/B_0")
        # then the new path should be /B/B_0
        assert self.ws.get_current_collection() == "b_0"