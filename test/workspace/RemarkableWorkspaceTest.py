import unittest

from src.workspace.RemarkableWorkspace import RemarkableWorkspace

class RemarkableWorkspaceTest(unittest.TestCase):

    def test_change_collection_from_root_to_direct_subpath(self):
        data = {
            "root": {"type": "CollectionType", "parent": "", "visibleName": ""},
            "a": {"type": "CollectionType", "parent": "", "visibleName": "A"},
        }
        ws = RemarkableWorkspace(data)
        ws.change_collection("/A")
        assert ws.get_current_collection() == "a"
