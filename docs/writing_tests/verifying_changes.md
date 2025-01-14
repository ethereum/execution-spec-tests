# Verifying Changes

The `tox` tool is used by execution-spec-tests to perform various checks on the codebase such as linting, type checking and spell-checking. The `tox` command can be executed locally to ensure that Github CI checks pass upon pushing to the repository.

!!! note "Using automatic pre-commit checks"
    Some `tox` environments can be ran as a git pre-commit hook, see [Enabling Pre-Commit Checks](../dev/precommit.md).

## Running `tox`

### Execution

Run all `tox` environments in parallel with:

```console
uvx --with=tox-uv tox run-parallel
```

or, with sequential test environment execution and verbose output as:

```console
uvx --with=tox-uv tox
```

As some environments are rather slow, the next section describes how to run them individually.

!!! note "Tox Virtual Environment"
    The checks performed by `tox` are sandboxed in their own virtual environments (which are created automatically in the `.tox/` subdirectory). These can be used to debug errors encountered during `tox` execution.

### Listing the Available Environments

Get a list of all the available `tox` environments:

```console
uvx --with=tox-uv tox -av
```

## Executing `tox` Environments Individually

A selection of preferred environments may be executed via the `-e` flag:

```console
uvx --with=tox-uv tox -e lint,typecheck,spellcheck
```

### Environments required for test case changes (`./tests/`)

```console
uvx --with=tox-uv tox -e lint,typecheck,spellcheck,tests-deployed
```

### Environments required for test framework and library changes (`./src/`)

```console
uvx --with=tox-uv tox -e lint,typecheck,spellcheck,pytest
```

### Environment required for documentation changes (`./docs/`)

```console
uvx --with=tox-uv tox -e spellcheck,markdownlint,mkdocs
```

### Additional Required Dependencies for `spellcheck` and `markdownlint`

The `spellcheck` and `markdownlint` environments require external (non-python) packages. To avoid disruption to external contributors, these environments run in a "soft fail" mode if these dependencies are not available.

Additional, optional prerequisites:

1. `pyspelling`:

    ```console
    sudo apt-get install aspell aspell-en
    ```

2. `markdownlint-cli2`:

    ```console
    sudo apt install nodejs
    sudo npm install markdownlint-cli2 --global
    ```

    Or use a specific node version using `nvm`, for example.

### Verifying Fixture Changes

When writing a PR that modifies either the framework or test cases, it is important to verify that the changes do not cause any issues with the existing test cases.

All filled fixtures contain a `hash` field in the `_info` object, which is the hash of the json string of the fixture. This hash can be used to verify that the fixture has not changed.

The `hasher` command can be used to bulk-verify the hashes of all fixtures in a directory.

It has the following options:

| Flag | Description |
|--------------|-------------|
| `--files` / `-f` | Prints a single combined hash per each JSON fixture file recursively contained in a directory. |
| `--tests` / `-t` | Prints the hash of every single test vector in every JSON fixture file recursively contained in a directory. |
| `--root` / `-r` | Prints a single combined hash for all JSON fixture files recursively contained in a directory. |

For a quick comparison between two fixture directories, the `--root` option can be used and if the output matches, it means the fixtures in the directories are identical:

```console
hasher --root fixtures/
hasher --root fixtures_new/
```

If the output does not match, the `--files` option can be used to identify which files are different:

```console
diff <(hasher --files fixtures/) <(hasher --files fixtures_new/)
```

And the `--tests` option can be used for an even more granular comparison:

```console
diff <(hasher --tests fixtures/) <(hasher --tests fixtures_new/)
```
