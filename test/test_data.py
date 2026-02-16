"""
    Module for shared test data. Programmers are encouraged to update
    the test data when needed, but it is good to keep in mind that
    updating test data may break existing test cases.
"""

from typing import Dict

TEST_DATA: Dict[str, Dict[str, str]] = {
            "": {"type": "CollectionType", "parent": "", "visibleName": ""},
            "a": {"type": "CollectionType", "parent": "", "visibleName": "A"},
            "a_0": {"type": "CollectionType", "parent": "a", "visibleName": "A_0"},
            "b": {"type": "CollectionType", "parent": "", "visibleName": "B"},
            "b_0": {"type": "CollectionType", "parent": "b", "visibleName": "B_0"},
        }