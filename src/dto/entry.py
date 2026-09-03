from dataclasses import dataclass

from src.dto.content import Content
from src.dto.metadata import Metadata


@dataclass
class Entry:
    metadata: Metadata
    content: Content
    size: int


