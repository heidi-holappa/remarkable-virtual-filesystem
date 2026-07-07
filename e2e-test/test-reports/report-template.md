# Test report

Release: 
Date: 
reMarkable device: 
Used test material: content of directory `test/`


## Test Suite: ls

* [ ] TC1: list directory content
  1. input: `cd test`
  2. input: `ls`
  3. expected outcome: all files and sub-directories in path `/test` should be listed
* [ ] TC2: list with args
  1. input: `cd test`
  2. input: `ls test_0`
  3. expected outcome: all files and sub-directories in path `/test/test_0/` 
  

## Test Suite: cd

* [ ] TC1: change directory with absolute path
  1. input: `cd /test/test_0/`
  2. expected outcome: directory now is `/test/test_0/`
* [ ] TC2: change directory without argument
  1. input: `cd /test/test_0/`
  2. input: `cd`
  3. expected outcome: directory is now root / home directory
* [ ] TC3: change directory with relative path
  1. input: `cd /test/test_0/`
  2. input: `cd ../test_1/`
  3. expected outcome: directory now is `/test/test_1/`
* [ ] TC4: change directory when directory name has whitespace
  1. input: `cd test`
  2. input: `cd 'test 3'`
  3. expected outcome: directory now is `/test/test 3/`
* [ ] TC5: change directory into current directory
  1. input: `cd test`
  2. input: `cd .`
  3. expected outcome: directory is now `/test/`
* [ ] TC6: change directory above root directory
  1. input: `cd ..` (in root)
  2. expected outcome: directory is now `/`
* [ ] TC7: change directory with multiple args
  1. input: `cd test test_0`
  2. expected outcome: descriptive error message instructing of usage

## Test Suite: help

* [ ] TC1: help without args
* [ ] TC2: help with command as an arg
* [ ] TC3: help with non-existing command as an arg


## Test Suite: rename

* [ ] TC1: rename a file
* [ ] TC2: rename a directory
* [ ] TC3: rename with invalid characters
* [ ] TC4: rename into a name that exist with the same parent


## Test Suite: move


* [ ] TC1: move a file
  1. input: `cd test`
  2. input: `mv document-0.pdf test_0`
  3. input: `ls test_0`
  4. expected outcome: file `document-0.pdf` is now in path `/test/test_0/`
  5. input: `mv /test/test_0/document-0.pdf /test/`
  3. input: `ls /test/`
  7. expected outcome: file `document-0.pdf` is now in path `/test/`
* [ ] TC2: move a path
  1. input: `cd test`
  2. input: `mv test_1 test_0`
  3. input: `ls test_0`
  4. expected outcome: path `test_1` is now in path `/test/test_0/`
  5. input: `mv /test/test_0/test_1 /test/`
  3. input: `ls /test/`
  7. expected outcome: directory `test_1` is now in path `/test/`
* [ ] TC3: move multiple items with wildcard
    1. input: `cd test`
    2. input: `mv document*.pdf test_0`
    3. input: `ls test_0`
    4. expected outcome: files `document-0.pdf` and `document-0.pdf` are now in path `/test/test_0/`
    5. input `ls /test/`
    6. expected outcome: `document-2.txt` is still in path `/test/`
    7. clean up:
      - input: `mv /test/test_0/document-0.pdf /test/`
      - input: `mv /test/test_0/document-1.pdf /test/`
* [ ] TC4: move non-existing file
  1. input: `cd test`
  2. input: `mv no-such-file.pdf test_0`
  3. expected outcome: descriptive error message informing of the failure

## Test Suite: remove

* [ ] TC1: remove a file that exists
* [ ] TC2: remove multiple files with a wildcard
* [ ] TC3: remove a directory
* [ ] TC4: remove directories and files with wildcard
* [ ] TC5: try to remove a file that does not exist

## Test Suite: mkdir

* [ ] TC1: mkdir with valid characters
* [ ] TC2: mkdir with invalid characters
* [ ] TC3: mkdir but directory with same name exists


## Test Suite: rcp (remote copy)


* [ ] TC1: Remote copy a single file
* [ ] TC2: Remote copy all documents in a directory
* [ ] TC3: Recursive remote copy
* [ ] TC4: Remote copy a file that does not exist
* [ ] TC5: Remote copy to a directory that does not exist
