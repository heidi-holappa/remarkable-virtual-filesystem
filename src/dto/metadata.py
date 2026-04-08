"""
    Module for a metadata entry.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Set, Any, Self

from src.constant import UUID_REGEX
from src.dto.entry_type_enum import EntityType
from src.exception.invalid_metadata_exception import InvalidMetadataException


@dataclass(slots=True)
class Metadata:
    created_time: int
    last_modified: int
    new: bool
    parent: str
    pinned: bool
    source: str
    type: EntityType
    visible_name: str

    def __post_init__(self) -> None:
        """
            Validates that the initialized data class
            is a valid representation of reMarkable
            metadata-file.
        """

        validation_errors: List[str] = []

        if not self._is_valid_epoch_in_milliseconds_field(self.created_time):
            validation_errors.append(f"createdTime: {self.created_time}")

        if not self._is_valid_epoch_in_milliseconds_field(self.last_modified):
            validation_errors.append(f"lastModified: {self.last_modified}")

        if not isinstance(self.new, bool):
            validation_errors.append(f"new: {self.new}")

        if not self._is_valid_uuid_field(self.parent):
            validation_errors.append(f"parent: {self.parent}")

        if not isinstance(self.pinned, bool):
            validation_errors.append(f"pinned: {self.pinned}")

        if not isinstance(self.source, str):
            validation_errors.append(f"source: {self.source}")

        if not isinstance(self.type, EntityType):
            validation_errors.append(f"type: {self.type}")

        if not isinstance(self.visible_name, str):
            validation_errors.append(f"visibleName: {self.visible_name}")


        if validation_errors:
            raise InvalidMetadataException(
                f"one or more metadata fields have invalid values: {','.join(validation_errors)}")

    # -------------------------------
    #   dictionary operations
    # -------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return reMarkable-compatible JSON structure."""
        return {
            "createdTime": self.created_time,
            "lastModified": self.last_modified,
            "new": self.new,
            "parent": self.parent,
            "pinned": self.pinned,
            "source": self.source,
            "type": self.type.value,
            "visibleName": self.visible_name,
        }

    @classmethod
    def from_dict(cls, metadata_dict: Dict[str, Any]) -> Self:
        """
        Tries to initialize an instance of Metadata from
        the provided dictionary. The dictionary may contain
        additional keys that are not present in metadata, and
        it MUST contain all keys that are present in metadata

        Raises:
            - InvalidMetadataException if the provided dictionary
                violates the validation rules of Metadata instance

        :param metadata_dict: a dictionary from which metadata is generated
        :return: an instance of metadata dataclass
        """

        required_fields = {
            "createdTime",
            "lastModified",
            "new",
            "parent",
            "pinned",
            "source",
            "type",
            "visibleName",
        }

        missing_fields: Set[str] = required_fields - set(metadata_dict.keys())

        if missing_fields:
            raise InvalidMetadataException(
                f"Missing metadata fields: {', '.join(sorted(missing_fields))}"
            )


        # --- enum casting ---
        try:
            entity_type = EntityType(metadata_dict["type"])
        except Exception as e:
            raise InvalidMetadataException(
                f"type: invalid value {metadata_dict['type']}"
            ) from e

        return cls(
        created_time=int(metadata_dict["createdTime"]),
        last_modified=int(metadata_dict["lastModified"]),
        new=metadata_dict["new"],
        parent=metadata_dict["parent"],
        pinned=metadata_dict["pinned"],
        source=metadata_dict["source"],
        type=entity_type,
        visible_name=metadata_dict["visibleName"],
        )

    # -------------------------------
    #   static validator methods
    # -------------------------------

    @staticmethod
    def _is_valid_epoch_in_milliseconds_field(value: int) -> bool:
        """validates given string is a valid epoch milliseconds field"""
        if not isinstance(value, int):
            return False

        now_ms = int(time.time() * 1000)
        return 0 <= value <= now_ms + 10_000

    @staticmethod
    def _is_valid_uuid_field(uuid_field: str) -> bool:
        """
            Validates the given field is either a valid UUID field
            or the root entry (empty string)
        """
        if not isinstance(uuid_field, str):
            return False
        return uuid_field == "" or bool(UUID_REGEX.match(uuid_field))


