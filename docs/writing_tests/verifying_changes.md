# Verifying Changes

The `tox` tool can be executed locally to check that local changes won't cause Github Actions Checks to fail.

!!! note "Pre-commit"
    Tox can be ran as a git pre-commit hook, see [Enabling Pre-Commit Checks](../dev/precommit.md).

## Executing `tox`

### Execution

Run `tox` and execute the defined environments (see `tox.ini`) in parallel with:

```console
uvx --with=tox-uv tox run-parallel
```

or, with sequential test environment execution and verbose output as:

```console
uvx --with=tox-uv tox
```

This executes all the environments described in the next section.

!!! note "Tox Virtual Environment"
    The checks performed by `tox` are sandboxed in their own virtual environments (which are created automatically in the `.tox/` subdirectory). These can be used to debug errors encountered during `tox` execution.

    Whilst we create a virtual environment in the code snippet above, it's only to install the tox tool itself.

## Executing `tox` Environments Individually

There are three tox environments available:

1. `framework`: Lint and test framework and libraries related code in `src/`.
2. `tests`: Lint and test the test cases in `tests/` (runs `fill` on all forks deployed to mainnet).
3. `docs`: Lint and spell-check markdown in `docs/`; build docs.

For targeted tox runs locally, each environment can be ran separately as described below.

### Test Case Verification: `tests`

Verify:

```console
uvx --with=tox-uv tox -e tests
```

### Framework Verification: `framework`

Verify:

```console
uvx --with=tox-uv tox -e framework
```

### Documentation Verification: `docs`

This environment runs `pyspelling` and `markdownlint-cli2` in a "soft fail" mode because they require external (non-python) packages. This allows developers who aren't working on documentation to execute tox locally without additional overhead. These commands are, however, ran as part of the checks in Github Actions.

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

Verify:

```console
uvx --with=tox-uv tox -e docs
```

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
