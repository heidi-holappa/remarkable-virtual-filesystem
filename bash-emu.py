from com.common import clear, ls, mv, rm
from typing import List
from com.help import help

while True:
    user_input: List[str] = input("remarkable$ ").split(' ')
    
    if not user_input:
        continue
    
    command, *args = user_input

    match command:
        case "clear":
            clear()
        case "ls":
            ls(args)
        case "mv":
            mv(args)
        case "help":
            help()
        case "exit" | "x":
            break
        case _:
            print("Unknown com. Type help for a list of supported commands")
