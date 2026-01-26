import subprocess
import tarfile, json
from io import BytesIO
from typing import Dict, Any, Optional

from constant import SSH_CONNECT, REMOTE_PREFIX

class RemarkableWorkspace:

    # Document and collection data loaded from reMarkable
    _data: Dict[str, Dict[str, Any]]
    # An empty string represents root.
    _current_collection: str

    def __init__(self):
        self._data: Optional[Dict[str, Dict[str, Any]]] = None
        self._current_collection: str = ''

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

    def load(self) -> None:
        """
        Loads the initial metadata information. If metadata is already
        loaded into class attribute, does nothing.

        :return: None
        """
        if self._data is None:
            self._data = self._fetch_to_memory()

    def get_data(self) -> Dict[str, Dict[str, Any]]:
        """
        A getter for the reMarkable filedata

        :return: a dictionary of Remarkable file data
        """
        self.load()
        return self._data  # type: ignore

    def refresh(self) -> None:
        self._data = self._fetch_to_memory()

    def get_current_collection(self) -> str:
        """
        A getter for the current collection. An empty string
        represents the root.

        :return: a UUID of the current collection
        """
        return self._current_collection

    def set_current_collection(self, collection: str) -> None:
        """
        Setter for the current collection. The collection
        must be either an UUID of a CollectionType or an
        empty string for root.

        :return: None
        """
        is_root = collection == ''
        is_valid_collection = self._data.get(collection) and self._data[collection].get('type') == 'CollectionType'
        if not (is_root or is_valid_collection):
            # TODO: think about this. Should this lead to exception or be handled more gracefully?
            raise Exception("Invalid Collection")
        self._current_collection = collection


    def get_parent(self) -> str:
        return self._data[self._current_collection].get('parent')

    def get_collection(self, collection: str) -> Optional[str]:
        """
        As a first version returns the uuid of the collection with the current parent
        and a matching visible name
        :param collection: a name of the collection
        :return: an optional UUID of the collection
        """
        for k, v in self._data.items():
            if v.get('parent') != self._current_collection:
                continue
            if v.get('type') == 'CollectionType' and v.get('visibleName') == collection:
                return k
        return None

    def get_current_path(self) -> str:
        if self._current_collection == '':
            return "/"
        return self.recurse_collection_path(self._current_collection)

    def recurse_collection_path(self, uuid: str) -> str:
        """
        A helper method to find the path for each entity.

        :param uuid: entity's uuid
        :param remarkable_metadata: a reference to the dictionary of metadata
        :return: a string representation of the path
        """

        if not self._data.get(uuid):
            return './<NA>'

        # print(f"data for {uuid}: {remarkable_metadata.get(uuid)}")
        if self._data[uuid].get('parent') == '':
            return "./" + self._data[uuid]['visibleName']

        if self._data[uuid].get('parent') == 'trash':
            return './trash/' + self._data[uuid].get('visibleName')

        return self.recurse_collection_path(self._data[uuid]['parent']) + "/" + self._data[uuid].get('visibleName')



remarkable_workspace = RemarkableWorkspace()