# Test report

Release:  
Date:  
reMarkable device:  
Used test material: content of directory `test/`  


## Test Suite: ls

* [x] TC1: list directory content
  0. start at root directory 
  1. input: `cd test`
  2. input: `ls`
  3. expected outcome: all files and sub-directories in path `/test` should be listed
* [x] TC2: list with args
  0. start at root directory 
  1. input: `cd test`
  2. input: `ls test_0`
  3. expected outcome: all files and sub-directories in path `/test/test_0/` 
* [x] TC3: list with invalid arg
  0. start at root directory 
  1. input: `ls /test/abc`
  2. expected outcome: descriptive message of no such path existing
  

## Test Suite: cd

* [x] TC1: change directory with absolute path
  0. start at root directory 
  1. input: `cd /test/test_0/`
  2. expected outcome: directory now is `/test/test_0/`
* [x] TC2: change directory without argument
  0. start at root directory 
  1. input: `cd /test/test_0/`
  2. input: `cd`
  3. expected outcome: directory is now root / home directory
* [x] TC3: change directory with relative path
  0. start at root directory 
  1. input: `cd /test/test_0/`
  2. input: `cd ../test_1/`
  3. expected outcome: directory now is `/test/test_1/`
* [x] TC4: change directory when directory name has whitespace
  0. start at root directory 
  1. input: `cd test`
  2. input: `cd 'test 3'`
  3. expected outcome: directory now is `/test/test 3/`
* [x] TC5: change directory into current directory
  0. start at root directory 
  1. input: `cd test`
  2. input: `cd .`
  3. expected outcome: directory is now `/test/`
* [x] TC6: change directory above root directory
  0. start at root directory 
  1. input: `cd ..` (in root)
  2. expected outcome: directory is now `/`
* [x] TC7: change directory with multiple args
  0. start at root directory 
  1. input: `cd test test_0`
  2. expected outcome: descriptive error message instructing of usage

## Test Suite: help

* [x] TC1: help without args
  1. input: `help`
  2. expected outcome: list of available commands
* [x] TC2: help with command as an arg
  1. input `help mv`
  2. expected outcome: description of command move and supported arguments. Contains an example of usage
* [x] TC3: help with non-existing command as an arg
  1. input `help no-such-command`
  2. expected outcome: descriptive error message instructing of usage


## Test Suite: rename

* [x] TC1: rename a file
  0. start at root directory 
  1. input `cd test`
  2. input `rename document-0.pdf document-2.pdf`
  3. input `ls`
  4. expected outcome: `document-0.pdf` is not listed and `document-2.pdf` is listed
  5. reset:  
    a. input `rename document-2.pdf document-0.pdf`  
    b. confirm state reset with `ls`
* [x] TC2: rename a directory
  0. start at root directory 
  1. input `cd test`
  2. input `rename test_0 test_00`
  3. input `ls`
  4. expected outcome: `test_0` is not listed and `test_00` is listed
  5. reset:  
    a. input `rename test_00 test_0`  
    b. confirm state reset with `ls`
* [x] TC3: rename with invalid characters
  0. start at root directory 
  1. input `cd test`
  2. input `rename document-0.pdf @.pdf`
  3. expected outcome: descriptive error message informing of invalid characters
* [x] TC4: rename into a name that exist with the same parent
  0. start at root directory 
  1. input `cd test`
  2. input `rename document-0.pdf document-1.pdf`
  3. expected outcome: descriptive error message informing of file with same name existing


## Test Suite: move


* [x] TC1: move a file
  0. start at root directory 
  1. input: `cd test`
  2. input: `mv document-0.pdf test_0`
  3. input: `ls test_0`
  4. expected outcome: file `document-0.pdf` is now in path `/test/test_0/`
  5. state reset:  
    a. input: `mv /test/test_0/document-0.pdf /test/`  
    b. input: `ls /test/`  
    c. expected outcome: file `document-0.pdf` is now in path `/test/`  
* [x] TC2: move a path
  0. start at root directory 
  1. input: `cd test`
  2. input: `mv test_1 test_0`
  3. input: `ls test_0`
  4. expected outcome: path `test_1` is now in path `/test/test_0/`
  5. state reset:  
    a. input: `mv /test/test_0/test_1 /test/`  
    b. input: `ls /test/`  
    c. expected outcome: directory `test_1` is now in path `/test/`
* [x] TC3: move multiple items with wildcard
    0. start at root directory 
    1. input: `cd test`
    2. input: `mv document*.pdf test_0`
    3. input: `ls test_0`
    4. expected outcome: files `document-0.pdf` and `document-0.pdf` are now in path `/test/test_0/`
    5. input `ls /test/`
    6. expected outcome: `document-2.txt` is still in path `/test/`
    7. state reset:  
      a. input: `mv /test/test_0/document-0.pdf /test/`  
      b. input: `mv /test/test_0/document-1.pdf /test/`  
      c. confirm with `ls /test/`  
* [x] TC4: move non-existing file
  0. start at root directory 
  1. input: `cd test`
  2. input: `mv no-such-file.pdf test_0`
  3. expected outcome: descriptive error message informing of the failure

## Test Suite: remove

* [x] TC1: remove a file that exists
  1. input: `cd test`
  2. input: `rm document-0.pdf`
  3. expected outcome: `document-0.pdf` should no longer be listed with `ls`
  4. reset state:  
    a. remove directory `/test/`  
    b. remote copy e2e-test files to reMarkable  
* [x] TC2: remove multiple files with a wildcard
  1. input: `cd test`
  2. input: `rm *.pdf`
  3. expected outcome: no `pdf` files should be listed with `ls`
  4. reset state:  
    a. remove directory `/test/`  
    b. remote copy e2e-test files to reMarkable  
* [x] TC3: remove a directory
  1. input: `cd test`
  2. input: `rm test_0`
  3. expected outcome: path `test_0` is no longer listed with `ls`
  4. reset state:  
    a. remove directory `/test/`  
    b. remote copy e2e-test files to reMarkable
* [x] TC4: remove directories and files with wildcard
  1. input: `cd test`
  2. input: `rm *`
  3. expected outcome: no files or paths should be listed with `ls`
  4. reset state:  
    a. remove directory `/test/`  
    b. remote copy e2e-test files to reMarkable  
* [x] TC5: try to remove a file that does not exist
  1. input: `cd test`
  2. input: `rm does-not-exist.txt`
  3. expected outcome: descriptive error message informing of no such file found


## Test Suite: mkdir

* [x] TC1: mkdir with valid characters
  1. input: `cd test`
  2. input: `mkdir abc`
  3. expected outcome: path `abc` is listed with `ls`
  4. reset state:
    1. remove created path: `rm /test/abc/`
* [x] TC2: mkdir with invalid characters
  1. input: `cd test`
  2. input: `mkdir @`
  3. expected outcome: descriptive message informing of invalid characters
* [x] TC3: mkdir but directory with same name exists
  1. input: `cd test`
  2. input: `mkdir test_0`
  3. expected outcome: descriptive message informing of path already existing



## Test Suite: rcp (remote copy)


* [x] TC1: Remote copy a single file
  1. input: `rcp /path/to/project/e2e-test/test/document-0.pdf /` 
  2. expected outcome: `ls` in root path lists `document-0.pdf`
  3. reset state:  
    a. input: `rm /document-0.pdf`  
* [x] TC2: Remote copy all documents in a directory
  1. input: `rcp -a /path/to/project/e2e-test/test/ /` 
  2. expected outcome: `ls` in root path lists `document-0.pdf` and `document-1.pdf`
  3. reset state:  
    a. input: `rm /document-0.pdf`  
    b. input: `rm /document-1.pdf`
* [x] TC3: Recursive remote copy
  0. preparation: `rm /test/`
  1. input: `rcp -r /path/to/project/e2e-test/ /` 
  2. expected outcome: all paths and supported document types are copied to root path from provided host path
* [x] TC4: Remote copy a file that does not exist
  1. input: `rcp /path/to/project/e2e-test/test/no-such-document.pdf /` 
  2. expected outcome: descriptive message of no such file existing
* [x] TC5: Remote copy to a directory that does not exist
  1. input: `rcp /path/to/project/e2e-test/test/document-0.pdf /does-not-exist/` 
  2. expected outcome: descriptive message of target path not existing


## Test Suite: refresh

* [x] TC1: Refresh restarts xochitl.service
  1. input: `refresh`
  2. expected outcome: xochitl.service restarts. Verify this from the GUI application on reMarkable and on systemctl (e.g. `systemctl status xochitl.service`). 

## Test Suite: exit

* [x] TC1: Exit app with long command
  1. input: `exit`
  2. expected outcome: command exits the remarkable-vfs application
* [x] TC2: Exit app with short command
  1. input: `x`
  2. expected outcome: command exits the remarkable-vfs application