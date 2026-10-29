"""
Implementation of remote copy command used to
copy files from host machine to reMarkable
e-reader
"""

import os
import time

from src.dto.metadata import Metadata
from src.dto.content import Content
from src.dto.entry_type_enum import EntityType

from src.exception import (
    InvalidArgumentError,
    NotFoundError,
    InvalidMetadataError,
    InvalidContentError
)

from .base_command import BaseCommand

# pylint: disable=too-few-public-methods
class RemoteCopyCommand(BaseCommand):
    """
    Implementation of remote copy command used to
    copy files from host machine to reMarkable
    e-reader
    """

    def handle(self, args: list[str]) -> None:
        """
        Remote copy (rcp) copies either one PDF or EPUB file from host
        machine (user's computer running the python script) or all files
        in provided host directory to the target machine (reMarkable).

        Both source path and target collection must be provided with
        absolute paths, noting that the target path must be the absolute
        path in context of this application (i.e., the file structure
        shown in Xochitl GUI application), meaning that root path is '/',
        path to directory 'foo' whose parent is root is '/foo' or '/foo/'
        and so on.

        Usages:
          - rcp <source file> <target collection>
          - rcp -a <source_path> <target collection>

        :param args: source file and target collection
        """



        if len(args) == 2:
            operand_source, operand_target = args
            self._process_rcp_command_without_options(
                source_file=operand_source,
                target_collection=operand_target)
        elif len(args) > 2:
            self._process_rcp_with_options(args)
        else:
            print("rcp: usage: rcp <source file> <target collection>")

    # -------------------------
    # rcp
    # -------------------------
    def _process_rcp_with_options(self, utility_args: list[str]) -> None:
        """
        Handles rcp command with options. Flags are meant for
        copying multiple files with one command. This method
        validates the arguments, resolves a list of
        files to be copied and then for each file invokes
        `process_rcp_command` separately

        :param utility_args: list of utility arguments
        """

        try:
            # options MUST precede source_path and target_path
            options: list[str] = utility_args[:-2]

            if len(options) > 1 or not self._has_only_valid_options(options):
                raise InvalidArgumentError(
                    f"invalid options: {','.join(options)}: hint: help rcp")

            # The source and target MUST be the last two arguments
            source_path, target_collection = utility_args[-2:]

            target_uuid: str | None = self._traverse_path(target_collection)
            validated_target_uuid = self._validate_source_and_target_uuid(
                source_path, target_collection, target_uuid)

            recurse = options[0] == "-r"

            files_to_copy: list[str] = self._find_all_pdf_and_epub_files_in_path(
                source_path, recurse)

            if not files_to_copy:
                print(f"rcp: no pdf or epub files found in directory: {source_path}")
                return

            files_and_parents: list[tuple[str, str]] = (
                self._generate_target_path_uuid_and_source_file_pairs(
                    source_path, files_to_copy, validated_target_uuid))

            print(f"found {len(files_to_copy)} files to copy. copying files one-by-one."
                  f"\nDO NOT disconnect reMarkable while operation is ongoing.")
            for idx, file_parent_pair in enumerate(files_and_parents):
                source_file, parent_uuid = file_parent_pair
                self._copy_file_from_host_to_target(source_file, parent_uuid)
                print(f"{idx + 1}/{len(files_to_copy)}: "
                      f"{source_file} copied to {target_collection}")

            self._repository.refresh_data()

        except (InvalidArgumentError, NotFoundError) as e:
            print(f"rcp: {e}")

    def _process_rcp_command_without_options(
            self, source_file: str, target_collection: str) -> None:
        """
        Copies a single file defined by the user as the
        source file to the target collection in reMarkable
        device.

        :param source_file: absolute path of a PDF or EPUB file
        :param target_collection: absolute path of the target collection
        """

        try:

            target_uuid: str | None = self._traverse_path(target_collection)
            validated_target_uuid = self._validate_source_and_target_uuid(
                source_file, target_collection, target_uuid)

            self._copy_file_from_host_to_target(source_file, validated_target_uuid)

            self._repository.refresh_data()

        except NotFoundError as e:
            print(f"rcp: {e}")



    @staticmethod
    def _has_only_valid_options(options: list[str]) -> bool:
        """
        Starting from milestone v0.3 rcp supports
        flags (a)ll and (r)ecursive
        """
        valid_options = ['-a', '-r']
        for op in options:
            if op not in valid_options:
                return False
        return True


    @staticmethod
    def _validate_source_and_target_uuid(source: str,
                                         target_collection: str,
                                         target_uuid: str | None) -> str:
        if not os.path.exists(source):
            raise NotFoundError(f"rcp: source file {source} not found")
        if target_uuid is None:
            raise NotFoundError(f"rcp: target path {target_collection} not found")

        return target_uuid

    @staticmethod
    def _find_all_pdf_and_epub_files_in_path(path: str, recurse: bool) -> list[str]:
        """
        Walks through the path in host and collects all source
        documents. With recurse flag also walks child paths

        :param path: host path to walk
        :param recurse: is the walk recursive
        :return: a list of absolute paths
        """
        result = []

        for dirpath, _, filenames in os.walk(path):
            for file in filenames:
                if file.lower().endswith((".pdf", ".epub")):
                    result.append(os.path.abspath(os.path.join(dirpath, file)))
            if not recurse:
                break

        return result


    def _generate_target_path_uuid_and_source_file_pairs(
            self, source_path: str,
            files: list[str],
            target_collection: str) -> list[tuple[str, str]]:
        """
        Iterates through files and if needed, creates missing child
        collections to reMarkable in case of recursive remote copy.

        Raises: called function _get_or_create_collection may raise
        RemarkableWriteError which must be handled by the callee.

        :param source_path: the absolute path from which files are copied
        :param files: absolute path to each file
        :param target_collection: the target path to copy files into
        :return: list of tuples with parent uuid and path to file
        """

        result: list[tuple[str, str]] = []

        for abs_path in files:
            rel_path = abs_path.removeprefix(source_path).removeprefix('/')
            dirs_and_filename: list[str] = rel_path.split('/')
            # Note: the last element contains the filename:
            # filename: str = dirs_and_filename[-1:][0]
            dirs: list[str] = dirs_and_filename[:-1]
            parent = target_collection
            for directory in dirs:
                if not directory:
                    continue
                dir_uuid = self._get_or_create_collection(parent, directory)
                parent = dir_uuid
            result.append((abs_path, parent))
        return result


    def _get_or_create_collection(self, parent: str, child_visible_name: str) -> str:
        """
        Either gets a collection with a given visible name and parent,
        or creates the collection.

        Raises: invoked function may raise MetadataWriteError. Callee
                must handle this.

        :param parent: UUID of the parent
        :param child_visible_name: visible name of the collection
        :return: UUID of the collection
        """

        if self._parent_has_child_path_with_given_name(parent, child_visible_name):
            for entry_uuid, entry in self._repository.get_data().items():
                if (entry.metadata.visible_name == child_visible_name and
                        entry.metadata.parent == parent):
                    return entry_uuid

        new_entry_uuid: str =  self._create_collection_metadata_and_invoke_write(
            parent, child_visible_name)

        return new_entry_uuid



    def _copy_file_from_host_to_target(self, source_file: str, target_uuid: str) -> None:
        """
        Remote copy (rcp) command moves one file from host machine
        to the provided collection on the target machine (reMarkable).
        The source must be an absolute path to a file and the target
        must be an absolute path to a collection.


        :param source_file: source from which to copy
        :param target_uuid: target collection UUID
        """

        try:
            filename: str = os.path.basename(source_file)
            # splitext return extension with dot. We want to remove that here.
            file_extension: str = os.path.splitext(filename)[1][1:]

            content: Content = Content.from_dict(
                {"fileType": file_extension}
            )

            metadata: Metadata = Metadata(
                created_time=int(time.time()),
                last_modified=int(time.time()),
                new=False,
                parent=target_uuid,
                pinned=False,
                source="",
                type=EntityType.DOCUMENT_TYPE,
                visible_name=filename
            )

            print(f"SOURCE_FILE: {source_file}")

            self._repository.invoke_remote_copy(source_file=source_file,
                                     metadata=metadata, content=content)


        except (NotFoundError, InvalidMetadataError,
                InvalidContentError) as e:
            print(e)
