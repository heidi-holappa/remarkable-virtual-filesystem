# reMarkable Virtual Filesystem

A virtual filesystem for reMarkable. 

## Introduction

### Motivation

reMarkable stores each folder (collection) and document as a complex set of files. This makes advanced file operations over SSH cumbersome.

This program provides a virtual filesystem that mimics a POSIX-style structure and implements a curated subset of essential POSIX commands. This abstraction simplifies file management on the device. 

### Implementation

The commands are inspired by the POSIX specification (version 2024.1) but do not fully conform to it. Review the command documentation before use.

In addition to POSIX-like commands, the program supports copying documents from the host machine to the reMarkable device.   


### Documentation

Read this README carefully before use.  

See also: [Commands Wiki](https://github.com/heidi-holappa/remarkable-utilities/wiki/Commands)

### User responsibility

This is not an official reMarkable tool. Use it at your own risk.

You are responsible for reviewing the code and ensuring it is safe for your device. The author assumes no liability for any damage.

### Supported devices

Tested on reMarkable Paper Pro.

Compatibility with other models is likely but not guaranteed.

### System requirements

Host machine:
- Linux based OS  
- Python3 3.14+
- `ssh`, `tar`
- SSH config entry named remarkable

> To use a different SSH config name, update `SSH_CONNECT` in `src/constant.py`.

reMarkable device:
- SSH access configured
- `tar`

> Not tested on macOS, Windows, or WSL. 


## How to use

Read the documentation before starting.

Clone the repository (preferably from the `main` branch) or download a release.

Run:

```
python3 remarkable-vfs.py
```

## Development

Contributions are welcome.

The program runs on Python stdlib, but development requires additional dependencies. 

### Setup

Create a virtual environment:

```
python3 -m venv venv
```

Activate it:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements-dev.txt
```

> Review `requirements-dev.txt` before installing.


### Linting

```bash
pylint src/
```

### Testing

Run tests with coverage:  
```bash
coverage run --source=src -m pytest
```

View summary:  
```bash
coverage report
```

Generate HTML report:
```bash
coverage html
```

Run all and open report:

```bash
coverage run --source=src -m pytest && coverage html && coverage report && xdg-open htmlcov/index.html
```


### Contributions

Fork the repository, create a feature branch, and open a pull request.

Ensure your changes meet the [Definition of Done](./doc/dod.md). 