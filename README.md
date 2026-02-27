# Remarkable utilities

A repository for programs that provide convenience when operating with a reMarkable tablet.  

## Bash emulator

A bash-ish terminal emulation for operating with the user files in reMarkable. Portrays the user content in reMarkable as paths and singular files so that users can more conveniently do simple operations on files (list, move, remove). Additionally provides a command to copy files from local machine to the remarkable via SSH connection.  

Todo: 
- preparations
- how to run
- supported instructions



## Development


### Pylint

Execute pylint with 

```bash
pylint src/
```

### Testing

Create coverage data by running tests: 
```bash
coverage run --source=src -m pytest
```

View report overview in terminal: 
```bash
coverage report
```

Generate HTML-report:
```bash
coverage html
```

And for convenience: 
```bash
coverage run --source=src -m pytest && coverage html && coverage report && xdg-open htmlcov/index.html
```