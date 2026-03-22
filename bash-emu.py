import shlex
from src.com.common import clear, ls, mv, rm, cd
from typing import List
from src.com.help import help_instruction
from src.workspace.workspace_manager import default_workspace_manager as workspace_manager

def main_loop() -> None:

    ws = workspace_manager.get()

    while True:
        path = ws.get_current_path()
        user_input: List[str] = shlex.split(input(f"remarkable~{path}$ "))

        if not user_input:
            continue

        command, *args = user_input

        match command:
            case "cd":
                cd(args, workspace_manager)
            case "clear":
                clear()
            case "rm":
                rm(args, workspace_manager)
            case "ls":
                ls(args, workspace_manager)
            case "mv":
                mv(args, workspace_manager)
            case "help":
                help_instruction()
            case "exit" | "x":
                break
            case _:
                print("Unknown command. Type help for a list of supported commands")


if __name__ == "__main__":
    main_loop()