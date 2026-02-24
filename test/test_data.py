"""
    Module for shared test data. Programmers are encouraged to update
    the test data when needed, but it is good to keep in mind that
    updating test data may break existing test cases.
"""

from typing import Dict

UUID_A = "f6c6fa40-a38f-4b05-a31c-2a64bd6aed70"
UUID_A0 = "d066ef0a-e9ee-475d-a04d-c1f2be88768d"
UUID_B = "48635ee3-f8af-4013-98f3-7f2bfc2de0e4"
UUID_B0 = "52da29a9-96fd-47fc-bd7d-7eb825be10a3"
UUID_FAIRYTALE = "38e9f881-9cba-400d-b238-75c3bd6d64a8"
UUID_INVALID_LAST_MODIFIED = "5592fdc0-020c-4a69-b4d3-a3106ca328ca"


TEST_DATA: Dict[str, Dict[str, str]] = {
            "": {"type": "CollectionType", "parent": "", "visibleName": ""},
            UUID_A: {"type": "CollectionType", "parent": "", "visibleName": "A"},
            UUID_A0: {"type": "CollectionType", "parent": UUID_A, "visibleName": "A_0"},
            UUID_FAIRYTALE: {
                "type": "DocumentType",
                "parent": UUID_A,
                "visibleName": "Fairytale.pdf",
                "size": "1024 kB",
                "createdTime": 0,
                "lastModified": 123456789,
                "new": False,
                "pinned": False,
                "source": ""
            },
            UUID_INVALID_LAST_MODIFIED: {
                "type": "DocumentType",
                "parent": UUID_A,
                "visibleName": "InvalidLastModified.pdf",
                "size": "1024 kB",
                "createdTime": 0,
                "lastModified": -1,
                "new": False,
                "pinned": False,
                "source": ""
            },
            UUID_B: {"type": "CollectionType", "parent": "", "visibleName": "B"},
            UUID_B0: {"type": "CollectionType", "parent": UUID_B, "visibleName": "B_0"},
        }