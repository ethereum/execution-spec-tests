# Code Standards

The Python code in the tests subdirectory `./tests` must fulfill the following checks:

|   | Command                 | Explanation                                                              |
|---|-------------------------|--------------------------------------------------------------------------|
| 1 | `fname8 tests`          | Spell check passes using the `./whitelist.txt` dictionary file.          |
| 2 | `isort tests --check --diff` | Python imports ordered and arranged according to isort's standards. |
| 3 | `black tests --check --diff` | Python source must be black-formatted.                              |
| 4 | `flake8 tests`          | Python lint and spell-checked.                                           |
| 5 | `mypy tests`            | Objects that provide typehints pass type-checking via mypy.              |
| 6 | `fill`                  | All tests must execute correctly.                                        |
| 7 | `mkdocs build --strict` | Documentation generated without warnings.                                |
| 8 | `pyspelling`            | Markdown spell-check.                                                    |
| 9 | `markdownlint-cli2`     | Markdown lint check.                                                     |

While this seems like a long list, a correctly configured editor (see [VS Code Setup](../getting_started/setup_vs_code.md)) essentially assures:

1. Points 2 and 3 are automatically covered.
2. Points 1, 4, 5, 8 & 9 are mostly covered. Additionally, if you skip type hints, they won't be checked; we can help you add these in the PR.

These checks must pass in order for the execution-spec-tests Github Actions to pass upon pushing to remote.

!!! info "Running the checks with tox"
    All these checks can be executed locally in a single command, `tox`, see [Verifying Changes](./verifying_changes.md).

    If you need help, [get in touch](../getting_started/getting_help.md)!
