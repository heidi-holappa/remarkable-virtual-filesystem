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


## Test Suite: rename


## Test Suite: move


## Test Suite: remove


## Test Suite: mkdir

## Test Suite: rcp (remote copy)

