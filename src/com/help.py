def help():
    print(
"""
Supported commands:
  - clear:
      * clear screen
  - ls:   
      * list files in current path
      * supported args:
          -a: show all files
          -l: show files as a list
          -h: human readable size information
  - mv <target-path> <destination path>:   
      * move files from target path to destination path.
      * no supported arguments
  - help: 
      * show this help text
      * no supported arguments
  - e(x)it:
      * exit python program
""")

