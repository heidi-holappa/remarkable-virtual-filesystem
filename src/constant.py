"""
    Constant values for the reMarkable bash-emulator project
"""
import re
from typing import List



SSH_CONNECT: List[str] = ["ssh", "remarkable"]
SSH_REMOTE_HOST: str = "remarkable"
REMARKABLE_FILE_PATH: str = "/home/root/.local/share/remarkable/xochitl"
REMOTE_PREFIX: str = "cd /home/root/.local/share/remarkable/xochitl && "
REMOTE_UPDATE_XOCHITL = " && systemctl restart xochitl"
ROOT_COLLECTION: str = ''

COLLECTION_NOT_FOUND: str = "Collection with the given UUID was not found"
PARENT_NOT_FOUND: str = "Parent for entity not found. Parent UUID: {parent}, entity UUID: {entity}"
INVALID_PATH: str = 'The given path does not exist'
NO_SUCH_FILE_OR_DIRECTORY: str = 'No such file or directory'
NOT_A_DIRECTORY: str = 'Not a directory'

LS_COLUMN_WIDTH: int = 16


UUID_REGEX = re.compile(
        r"^[0-9a-f]{8}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{12}$"
    )
