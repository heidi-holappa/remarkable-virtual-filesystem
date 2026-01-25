import subprocess
import tarfile, json
from io import BytesIO
from typing import Dict, Any, Optional

from constant import SSH_CONNECT, REMOTE_PREFIX

class RemarkableFileData:

    _data: Dict[str, Dict[str, Any]]



    def __init__(self):
        self._data: Optional[Dict[str, Dict[str, Any]]] = None

    def load(self) -> None:
        if self._data is None:
            self._data = self._fetch_to_memory()


    def _fetch_to_memory(self) -> Dict[str, Dict[str, Any]]:
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
                    .removesuffix(".remarkable_file_data")
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

        Uses common tools such as du, awk and split found in
        BusyBox to gather the information.

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


    def get_data(self) -> Dict[str, Dict[str, Any]]:
        """
        A getter for the reMarkable filedata

        :return: a dictionary of Remarkable file data
        """
        self.load()
        return self._data  # type: ignore

    def refresh(self) -> None:
        self._data = self._fetch_to_memory()


    def generate_path_structure(self, metadata: Dict)  -> Dict:
        # TODO: is this necessary
        return {}