"""
    Constant values for the reMarkable bash-emulator project
"""
import re
from typing import List



SSH_CONNECT: List[str] = ["ssh", "remarkable"]
REMOTE_PREFIX: str = "cd /home/root/.local/share/remarkable/xochitl && "
ROOT_COLLECTION: str = ''

COLLECTION_NOT_FOUND: str = "Collection with the given UUID was not found"
INVALID_PATH: str = 'The given path does not exist'


UUID_REGEX = re.compile(
        r"^[0-9a-f]{8}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{12}$"
    )