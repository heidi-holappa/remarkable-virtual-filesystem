import subprocess
import tarfile, json
from io import BytesIO
from typing import Dict, Any

from constant import SSH_CONNECT, REMOTE_PREFIX

def fetch_all_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Fetches the file content for each metadata-file in the filepath
    for user files in reMarkable. Uses common tools found in the
    BusyBox to find and archive metadata content for transfer.

    The processing of fetched data is done by the Python application.

    :return: a dictionary of nested dictionaries each containing
                a metadata entry for a given entity, identified by
                the entitys UUID as dictionary key.
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
        raise RuntimeError("No metadata files found or tar produced no output")

    metadata: Dict = {}

    with tarfile.open(fileobj=BytesIO(tar_bytes), mode="r:") as tar:
        for member in tar:
            f = tar.extractfile(member)
            if not f:
                continue

            try:
                data: Dict = json.load(f)
            except json.JSONDecodeError:
                continue

            entry_uuid: str = member.name.removeprefix('./').removesuffix('.metadata')
            metadata[entry_uuid] = data

    sizes = get_file_sizes()
    for uuid, size in sizes.items():
        if uuid in metadata:
            metadata[uuid]['size'] = size

    return metadata


def get_file_sizes() -> Dict[str, int]:
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
