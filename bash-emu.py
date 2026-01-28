from com.common import clear, ls, mv, rm, cd
from typing import List
from com.help import help
from util.RemarkableWorkspace import remarkable_workspace as workspace

while True:
    path = workspace.get_current_path()
    user_input: List[str] = input(f"remarkable~{path}$ ").split(' ')
    
    if not user_input:
        continue
    
    command, *args = user_input

    match command:
        case "cd":
            cd(args)
        case "clear":
            clear()
        case "rm":
            rm(args)
        case "ls":
            ls(args)
        case "mv":
            mv(args)
        case "help":
            help()
        case "exit" | "x":
            break
        case _:
            print("Unknown command. Type help for a list of supported commands")
