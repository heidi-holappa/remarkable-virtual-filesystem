import subprocess
from typing import List, Dict

from util.RemarkableWorkspace import remarkable_workspace as workspace

def cd(args: List[str]) -> None:
    path = ''
    if args:
        path = ' '.join(args)
    match path:
        case "":
            workspace.set_current_collection('')
        case "..":
            workspace.set_current_collection(workspace.get_parent())
        case _:
            collection = workspace.get_collection(path)
            if collection:
                workspace.set_current_collection(collection)
            else:
                print("Invalid path")

def mv(args: List[str]) -> None:
    """
    A light implementation of move command

    TODO: implement mv

    :param args: arguments given for the instruction
    :return:
    """
    print("TODO: move stuff")


def rm(args: List[str]) -> None:
    """
    A light implementation of remove command.

    TODO: implement rm

    :param args: possible arguments
    :return: None
    """
    print("TODO: remove stuff")

def ls(args: List[str]) -> None:
    """
    A light implementation of the list command.

    TODO: add support for args

    :param args: arguments for the ls command
    :return: None
    """
    remarkable_metadata = workspace.get_data()

    result = []
    for uuid, v in remarkable_metadata.items():
        if remarkable_metadata[uuid].get('parent') != workspace.get_current_collection():
            continue
        path_and_file = recurse_path(uuid, remarkable_metadata)
        if remarkable_metadata[uuid].get('size'):
            path_and_file = str(remarkable_metadata[uuid].get('size')) + '\t' + path_and_file
        result.append(path_and_file)

    for e in sorted(result):
        print(e)

def clear():
    subprocess.run("clear")



def recurse_path(uuid: str, remarkable_metadata: Dict) -> str:
    """
    A helper method to find the path for each entity.

    TODO: remove when code uses workspace implementation of this

    :param uuid: entity's uuid
    :param remarkable_metadata: a reference to the dictionary of metadata
    :return: a string representation of the path
    """

    if not remarkable_metadata.get(uuid):
        return './<NA>'

    # print(f"data for {uuid}: {remarkable_metadata.get(uuid)}")
    if remarkable_metadata[uuid].get('parent') == '':
        return "./" + remarkable_metadata[uuid]['visibleName']

    if remarkable_metadata[uuid].get('parent') == 'trash':
        return './trash/' + remarkable_metadata[uuid].get('visibleName')

    return  recurse_path(remarkable_metadata[uuid]['parent'], remarkable_metadata) + "/" + remarkable_metadata[uuid].get('visibleName')