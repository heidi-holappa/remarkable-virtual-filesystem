"""
    Module providing an implementation of MetadataSource
    responsible for interacting with the reMarkable device
    via SSH connection
"""

import subprocess
import re
import time
import tarfile
import json
from typing import Dict, Any
from io import BytesIO
from collections.abc import Callable

from src.data.metadata_source import MetadataSource
from src.constant import REMOTE_PREFIX, SSH_CONNECT
from src.exception.remarkable_write_exception import RemarkableWriteException
from src.exception.invalid_metadata_exception import InvalidMetadataException

class RemarkableSSHMetadataSource(MetadataSource):
    """
        An implementation of MetadataSource responsible for
        interacting with the reMarkable device via SSH connection
    """

    _UUID_REGEX = re.compile(
        r"^[0-9a-f]{8}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{12}$"
    )

    def load(self) -> Dict[str, Dict[str, Any]]:
        """
        A public method to load metadata into memory
        :return: a dictionary of metadata
        """
        data = self._fetch_metadata()
        sizes = self._get_file_sizes()
        for uuid, size in sizes.items():
            if uuid in data:
                data[uuid]["size"] = size
        return data

    def _fetch_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetches the content of each *.metadata file in the filepath
        for user files in reMarkable. Uses common tools found in the
        BusyBox to find and archive remarkable_file_data content for transfer.

        In addition to metadata the size of all user file entities is stored
        with the metadata.

        """
        cmd: str = (
            REMOTE_PREFIX +
            "find . -name '*.metadata' -exec tar -cf - {} +"
        )

        proc = subprocess.Popen(
            SSH_CONNECT + [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        tar_bytes, stderr = proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(stderr.decode())

        if not tar_bytes:
            raise RuntimeError(
                f"No metadata files found.\n"
                f"Command: {cmd}\n"
                f"stderr: {stderr.decode()}"
            )

        data: Dict[str, Dict[str, Any]] = {}

        with tarfile.open(fileobj=BytesIO(tar_bytes), mode="r:") as tar:
            for member in tar:
                f = tar.extractfile(member)
                if not f:
                    continue

                try:
                    metadata = json.load(f)
                except json.JSONDecodeError:
                    continue

                uuid = (
                    member.name
                    .removeprefix("./")
                    .removesuffix(".metadata")
                )
                data[uuid] = metadata

        sizes = self._get_file_sizes()
        for uuid, size in sizes.items():
            if uuid in data:
                data[uuid]["size"] = size

        return data



    def _get_file_sizes(self) -> Dict[str, int]:
        """
        Fetches the combined size of all files and paths
        related to given entity for all entities in the
        reMarkable path for user files. The motivation is
        to provide intuition on the total disk space allocated
        to each entity, including the possible user notations.

        Uses common tools such as ``du``, ``awk`` and ``split``
        found in BusyBox to gather the information.

        :return: a dictionary with entity UUIDs as keys and
                    disk space allocated to each entity in kilobytes
        """
        cmd: str = (
                REMOTE_PREFIX +
                "du -s * | "
                "awk '"
                "{ split($2, a, \".\"); size[a[1]] += $1 } "
                "END { for (u in size) printf \"%s\\t%d\\n\", u, size[u] }"
                "'"
        )

        proc = subprocess.Popen(
            SSH_CONNECT + [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(stderr)

        sizes: Dict[str, int] = {}

        for line in stdout.splitlines():
            uuid, size = line.split("\t")
            sizes[uuid] = int(size)

        return sizes

    def write_metadata_to_remarkable(self, entry_uuid: str, metadata: Dict[str, str]) -> None:
        """Write metadata file to reMarkable

        Writes the provided metadata dictionary into reMarkable user file
        directory in a file named ``<uuid>.metadata``. A possible existing
        file on the device is overwritten.

        raises:
          **RemarkableWriteException**: indicates an exception occurred during write operation
          **InvalidMetadataException**: the provided metadata was invalid.

        :param entry_uuid: the UUID for which a metadata-file is to be written
        :param metadata: a dictionary containing metadata
        :return: None
        """

        if not self.is_valid_metadata(metadata):
            raise InvalidMetadataException(
                f"The metadata was invalid: {metadata}"
            )

        metadata_filename = f"{entry_uuid}.metadata"
        metadata_content = json.dumps(metadata, indent=4)

        cmd = REMOTE_PREFIX + f"cat > '{metadata_filename}'"

        try:
            with subprocess.Popen(
                    SSH_CONNECT + [cmd],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
            ) as proc:

                stdout, stderr = proc.communicate(metadata_content)

                if proc.returncode != 0:
                    raise RemarkableWriteException(
                        f"Failed to write metadata: {stderr.strip()}"
                    )

        except OSError as e:
            raise RemarkableWriteException(
                f"OS error while writing metadata: {e}"
            ) from e


    def is_valid_metadata(self, metadata: Dict[str, str]) -> bool:
        """Validates a metadata entry

        Validates that the given dictionary is a valid representation
        of reMarkable metadata-file.

        To be valid:
          1. Each metadata field must exist and have valid data entries.
          2. The dictionary contains no other fields.

        :param metadata: a dictionary representation of a metadata entry
        :return: boolean result for validation
        """

        valid_fields: Dict[str, Callable[[str], bool]] = {
            "createdTime": self._is_valid_epoch_in_milliseconds_field,
            "lastModified": self._is_valid_epoch_in_milliseconds_field,
            "new": self._is_valid_boolean_metadata_field,
            "parent": self._is_valid_uuid_field,
            "pinned": self._is_valid_boolean_metadata_field,
            "source": self._is_valid_string_field,
            "type": self._is_valid_metadata_type_field,
            "visibleName": self._is_valid_string_field
        }

        if set(metadata.keys()) != set(valid_fields.keys()):
            print(f"ERROR: metadata entry has invalid keys: {metadata}")
            return False


        for key, validator in valid_fields.items():
            value = metadata.get(key)
            if value is None or not validator(value):
                print(f"ERROR: invalid value in metadata field {key}: {value}")
                return False

        return True


    def _is_valid_boolean_metadata_field(self, boolean_field: str) -> bool:
        """Validates a boolean metadata field"""
        return isinstance(boolean_field, bool)

    def _is_valid_epoch_in_milliseconds_field(self, epoch_field: str) -> bool:
        """validates given string is a valid epoch milliseconds field"""
        if not isinstance(epoch_field, str):
            return False

        if not epoch_field.isdigit():
            return False

        # As the value is in milliseconds, we expect it to be atleast 13 digits in length
        if len(epoch_field) < 13:
            return False

        try:
            value = int(epoch_field)
        except ValueError:
            return False

        # crudely evaluate the value is reasonable
        now_ms = int(time.time() * 1000)
        if value < 0 or value > now_ms + 10_000:
            return False

        return True

    def _is_valid_string_field(self, str_field: str) -> bool:
        """validates the given field is a string field"""
        return isinstance(str_field, str)

    def _is_valid_uuid_field(self, uuid_field: str) -> bool:
        """
            Validates the given field is either a valid UUID field
            or the root entry (empty string)
        """
        if not isinstance(uuid_field, str):
            return False
        return uuid_field == "" or bool(self._UUID_REGEX.match(uuid_field))

    def _is_valid_metadata_type_field(self, type: str) -> bool:
        return type in ["CollectionType", "DocumentType"]

