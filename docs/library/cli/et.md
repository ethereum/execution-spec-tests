# `et` 👽

`et` is a CLI tool that helps with routine tasks. Invoke using `uv run et`.

## ⬛ `et make`

Groups several commands that generates project files for you. It includes:

### 1. `et make test`

Creates a new specification test file for an EIP.

Usage: `et make test [OPTIONS]`

Options:

- `--help` Show help and exit.

## ⬛ `et clean`

Remove all generated files and directories from the repository. If `--all` is
specified, the virtual environment and .tox directory will also be removed.

Note: The virtual environment and .tox directory are not removed by default.

Usage: `et clean [OPTIONS]`

Options:

- `--all` Remove the virtual environment as well.
- `--dry-run` Simulate the cleanup without removing files.
- `--help` Show help and exit.
