"""
    Module providing an implementation of MetadataSource
    responsible for interacting with the reMarkable device
    via SSH connection
"""

import subprocess
import tarfile
import json
from typing import Dict, Any
from io import BytesIO
from src.dto.metadata import Metadata

from src.data.metadata_source import MetadataSource
from src.constant import REMOTE_PREFIX, SSH_CONNECT
from src.exception.remarkable_write_exception import RemarkableWriteException

class RemarkableSSHMetadataSource(MetadataSource):
    """
        An implementation of MetadataSource responsible for
        interacting with the reMarkable device via SSH connection
    """

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


    def refresh(self) -> None:
        """
        Refresh will be implemented in ticket #25

        :return: None
        """
        raise NotImplementedError

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

    def write(self, entry_uuid: str, metadata: Metadata) -> None:
        """Write metadata file to reMarkable

        Writes the provided metadata dictionary into reMarkable user file
        directory in a file named ``<uuid>.metadata``. A possible existing
        file on the device is overwritten.

        raises:
          **RemarkableWriteException**: indicates an exception occurred during write operation

        :param entry_uuid: the UUID for which a metadata-file is to be written
        :param metadata: a Metadata DTO containing the metadata to be written
        :return: None
        """

        metadata_filename = f"{entry_uuid}.metadata"
        metadata_content = json.dumps(metadata.to_dict(), indent=4)

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
