"""
    Constant values for the reMarkable bash-emulator project
"""
from typing import List


SSH_CONNECT: List[str] = ["ssh", "remarkable"]
REMOTE_PREFIX: str = "cd /home/root/.local/share/remarkable/xochitl && "
ROOT_COLLECTION: str = ''

COLLECTION_NOT_FOUND: str = "Collection with the given UUID was not found"
INVALID_PATH: str = 'The given path does not exist'
