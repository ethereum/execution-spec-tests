# Code Standards

The Python code in the tests subdirectory `./tests` must fulfill the following checks:

|   | Command                 | Explanation                                                              |
|---|-------------------------|--------------------------------------------------------------------------|
| 1 | `ruff check tests`      | Python lint, format and imports check.                                   |
| 2 | `mypy tests`            | Objects that provide typehints pass type-checking via mypy.              |
| 3 | `fill`                  | All tests must execute correctly.                                        |
| 4 | `mkdocs build --strict` | Documentation generated without warnings.                                |
| 5 | `pyspelling`            | Markdown spell-check.                                                    |
| 6 | `markdownlint-cli2`     | Markdown lint check.                                                     |

A correctly configured editor (see [VS Code Setup](../getting_started/setup_vs_code.md)) will ensure that most points are resolved automatically upon file save.

Additionally, if you skip type hints, they won't be checked; we can help you add these in the PR.

These checks must pass in order for the execution-spec-tests Github Actions to pass upon pushing to remote.

!!! info "Running the checks with tox"
    All these checks can be executed locally in a single command, `tox`, see [Verifying Changes](./verifying_changes.md).

    If you need help, [get in touch](../getting_started/getting_help.md)!
