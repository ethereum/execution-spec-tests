# Verifying Changes

The `tox` tool can be executed locally to check that local changes won't cause Github Actions Checks to fail.

!!! note "Pre-commit"
    Tox can be ran as a git pre-commit hook, see [Enabling Pre-Commit Checks](../dev/precommit.md).

## Executing `tox`

### Prerequisites

```console
python -m venv ./venv/
source ./venv/bin/activate
pip install tox
```

### Execution

Run tox, as executed in Github Actions, with:

```console
tox
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
tox -e tests
```

### Framework Verification: `framework`

Verify:

```console
tox -e framework
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
tox -e docs
```
