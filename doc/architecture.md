# Project architecture


## Class structure

The class diagram details the structure and relationships of core classes, excluding exceptions. The structure is simple and information mainly flows to one direction only. User commands are parsed and evaluated by the main loop, which then invokes the logic to handle a specific command or informs user of invalid input. The `common.py` module does initial validation on user input and fails fast for generic cases (missing arguments, too many arguments). The core for command processing and data manipulation resides within `RemarkableWorkspace`. The `RemarkableSshMetadataSource` handles the communication with the reMarkable reader by invoking subprocesses and processing their responses.  

![class diagram](./remarkable-vfs-class-diagram.drawio.svg)



## Case study - remove command

This case study details the steps for the happy path of `rm` command (remove). User invokes the command with the argument `*.pdf` which leads to the removal of all documents with visible name ending in extension `PDF` from the current working directory. In this happy path case study information flows to one direction only, as there is no need to process the response from reMarkable device in any invoking layer. As can be seen, most of the logic resides within `RemarkableWorspace`, which collects `UUIDs` for matching entries and then with one subprocess invocation removes them all from the reMarkable device. The in-memory data structure is then updated (in `_data.pop(entry)`) to reflect the current state of the reMarkable device.  

![remove - happy path case study](./rm-sequence-diagram.drawio.svg)