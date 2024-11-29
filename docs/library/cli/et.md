## `et` 👽

`et` is a CLI tool that helps with routine tasks. Invoke using `uv run et`.

## ⬛ `et make`

Groups several commands that generates project files for you. It includes:

### 1. `et make test`

Creates a new specification test file for an EIP.

Usage: `et make test [OPTIONS]`

Options:

- `--help` Show help and exit.

## ⬛ `et clean`

Remove all generated files and directories from the repository.  
Note: The virtual environment is not removed by default.

Usage: `et clean [OPTIONS]`

Options:

- `--all` Remove the virtual environment as well.
- `--help` Show help and exit.
