"""
    Module providing an implementation of MetadataSource
    responsible for interacting with the reMarkable device
    via SSH connection
"""

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import uuid
from io import BytesIO
from typing import Dict, List, Any

from src.constant import (
    REMOTE_PREFIX, SSH_CONNECT,
    REMARKABLE_FILE_PATH, SSH_REMOTE_HOST)
from src.data.metadata_source import MetadataSource
from src.dto.content import Content
from src.dto.metadata import Metadata
from src.exception.remarkable_operation_exception import RemarkableOperationException
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
        for entry_uuid, size in sizes.items():
            if entry_uuid in data:
                data[entry_uuid]["size"] = size
        return data


    def write_metadata(self, entry_uuid: str, metadata: Metadata) -> None:
        """Write metadata file to reMarkable

        Writes the provided metadata dictionary into reMarkable user file
        directory in a file named ``<uuid>.metadata``. A possible existing
        file on the device is overwritten. After the write operation restarts
        the Xochitl process.

        raises:
          **RemarkableWriteException**: indicates an exception occurred during write operation

        :param entry_uuid: the UUID for which a metadata-file is to be written
        :param metadata: a Metadata DTO containing the metadata to be written
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

                _ , stderr = proc.communicate(metadata_content)

                if proc.returncode != 0:
                    raise RemarkableWriteException(
                        f"Failed to write metadata: {stderr.strip()}"
                    )

        except OSError as e:
            raise RemarkableWriteException(
                f"OS error while writing metadata: {e}"
            ) from e

    def remove(self, entity_uuids: List[str]) -> None:
        """
        Attempts to remove an entity with the given UUID
        from the reMarkable device. This operation is
        undoable and removes all files and paths with the
        given UUID as a suffix.

        Raises:
          - **RemarkableWriteException**: indicates an exception occurred during write operation

        :param entity_uuids: UUID of the entity to remove
        """

        if not entity_uuids:
            return

        patterns = [f"{item_uuid}*" for item_uuid in entity_uuids]
        removable_entities = " ".join(patterns)

        cmd = REMOTE_PREFIX + f"rm -rf -- {removable_entities}"
        try:
            with subprocess.Popen(
                    SSH_CONNECT + [cmd],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
            ) as proc:

                _, stderr = proc.communicate()

                if proc.returncode != 0:
                    raise RemarkableWriteException(
                        f"Failed to remove files: {stderr.strip()}"
                    )

        except OSError as e:
            raise RemarkableWriteException(
                f"OS error while removing files: {e}"
            ) from e


    def remote_copy(self, source_file: str,
                    metadata: Metadata, content: Content) -> None:
        """
        Attempts to copy a file from host machine to the
        target machine (reMarkable).

        :param source_file: absolute path to source file to be copied
        :param metadata: a metadata entry for the file
        :param content: a content entry for the file
        """

        entry_uuid: str = str(uuid.uuid4())

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                # copy source file with UUID filename
                filename: str = os.path.basename(source_file)
                uuid_filename: str = entry_uuid + os.path.splitext(filename)[1]

                target_file_path = os.path.join(tmp_dir, uuid_filename)
                shutil.copy(source_file, target_file_path)

                # write metadata + content
                metadata_file: str = os.path.join(tmp_dir, f"{entry_uuid}.metadata")
                content_file: str = os.path.join(tmp_dir, f"{entry_uuid}.content")

                with open(metadata_file, mode="w", encoding="utf-8") as file:
                    json.dump(obj=metadata.to_dict(), fp=file, indent=4)

                with open(content_file, mode="w", encoding="utf-8") as file:
                    json.dump(obj=content.to_dict(), fp=file, indent=4)

                # ---- Transfer using tar over ssh ----
                self._invoke_file_transfer(tmp_dir)

            except RemarkableWriteException as e:
                raise e

    @staticmethod
    def _invoke_file_transfer(tmp_dir: str) -> None:
        """
        Handles the two subprocesses required for file transfer. The
        implementation uses tar and ssh to keep the requirements
        of this program as minimal as possible. The motivation is
        that ssh is a base requirement for the program, and tar
        is commonly available out-of-the-box in Linux distributions.

        raises:
          - RuntimeError if ssh subprocess fails

        :param tmp_dir: the temporary directory for local files
        """
        tar_cmd = ["tar", "cf", "-", "-C", tmp_dir, "."]
        ssh_cmd = ["ssh", SSH_REMOTE_HOST, f"tar xf - -C {REMARKABLE_FILE_PATH}"]

        with subprocess.Popen(tar_cmd, stdout=subprocess.PIPE) as tar_proc:
            with subprocess.Popen(ssh_cmd, stdin=tar_proc.stdout) as ssh_proc:
                # Allow tar to receive SIGPIPE if ssh fails
                if tar_proc.stdout:
                    tar_proc.stdout.close()

                ssh_proc.communicate()

                if ssh_proc.returncode != 0:
                    raise RemarkableWriteException(
                        f"rcp: failed to copy file. subprocess return code: {ssh_proc.returncode}")

    @staticmethod
    def restart_xochitl() -> None:
        """
        Restarts the xochitl service on the remote reMarkable device via SSH.

        This is typically required after modifying files in the xochitl data
        directory for changes to take effect.

        :raises RemarkableOperationException: if the restart command fails
        """

        cmd = ["ssh", SSH_REMOTE_HOST, "systemctl restart xochitl"]

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RemarkableOperationException(
                f"Failed to restart xochitl:\n"
                f"STDOUT: {e.stdout}\n"
                f"STDERR: {e.stderr}"
            ) from e

    # ------------------------------
    # Private methods
    # -------------------------------

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

        with subprocess.Popen(SSH_CONNECT + [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,) as proc:


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

                entry_uuid = (
                    member.name
                    .removeprefix("./")
                    .removesuffix(".metadata")
                )
                data[entry_uuid] = metadata

        sizes = self._get_file_sizes()
        for e_uuid, size in sizes.items():
            if e_uuid in data:
                data[e_uuid]["size"] = size

        return data



    @staticmethod
    def _get_file_sizes() -> Dict[str, int]:
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

        with subprocess.Popen(
            SSH_CONNECT + [cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True) as proc:

            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                raise RuntimeError(stderr)

        sizes: Dict[str, int] = {}

        for line in stdout.splitlines():
            entry_uuid, size = line.split("\t")
            sizes[entry_uuid] = int(size)

        return sizes
