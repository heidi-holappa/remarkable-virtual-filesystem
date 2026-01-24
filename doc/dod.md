# Definition of Done

Guidelines for this project

- All new development should be based on a ticket detailing what is being done
  - each ticket should explain the motivation for the changes and the objectives based on which developers can reason when the issue has been fully resolved
  - development is done in feature branches which should be linked to the ticket
  - all commits should refer to the ticket. One [tutorial](https://gitdailies.com/articles/link-github-commit-to-issue/)
- Ideally all new code should be tested. This can however be difficult as this project uses subprocesses invoked by the script. Nevertheless, when designing new code, it should be designed so that as much as possible of the new code can be tested to verify the correct behavior
- All new code should have docstring or other documentation
- All new functionality should be documented and existing documentation should be updated
- Once all objectives of an issue and DoD are met, a PR should be opened. After a careful review of the PR, changes should be merged into dev 