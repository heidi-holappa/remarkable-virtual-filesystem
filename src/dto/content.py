"""
    Module for content entry

    Note: the module structure was copied from metadata.py
    For the 0.1 release, the structure is quite heavy for,
    as .content -files only have one field. In the future,
    they may support more fields and in that case this
    structure provides a more mature foundation.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Self, Set

from src.dto.file_type_enum import FileType
from src.exception.invalid_content_exception import InvalidContentException


@dataclass(slots=True)
class Content:
    file_type: FileType


    def __post_init__(self) -> None:
        """
        Validates the initialized content instance
        :return: None
        """

        validation_errors: List[str] = []

        if not isinstance(self.file_type, FileType):
            validation_errors.append("fileType for content file must be an Enum FileType")
        elif self.file_type.value not in ("pdf", "epub"):
            validation_errors.append("fileType for content file must be either pdf or epub")

        if validation_errors:
            raise InvalidContentException(
                f"one or more fields for .content file have invalid values: {','.join(validation_errors)}")


    # -------------------------------
    #   dictionary operations
    # -------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return reMarkable-compatible JSON structure."""
        return {
            "fileType": self.file_type.value,
        }

    @classmethod
    def from_dict(cls, content_dict: Dict[str, Any]) -> Self:
        """
        Tries to initialize an instance of Content file from
        the provided dictionary. The dictionary may contain
        additional keys that are not present in content-file,
        and it MUST contain all keys that are present in
        content file.

        Raises:
            - InvalidContentException if the provided dictionary
                violates the validation rules of Content instance

        :param content_dict: a dictionary from which content is generated
        :return: an instance of content dataclass
        """

        required_fields = {
            "fileType"
        }

        missing_fields: Set[str] = required_fields - set(content_dict.keys())

        if missing_fields:
            raise InvalidContentException(
                f"Missing content fields: {', '.join(sorted(missing_fields))}"
            )

        # --- enum casting ---
        try:
            file_type = FileType(content_dict["fileType"])
        except Exception as e:
            raise InvalidContentException(
                f"fileType: invalid value {content_dict['fileType']}"
            ) from e

        return cls(
            file_type=file_type
        )