# Verifying Changes

The `tox` tool can be used to lint, type check, test and verify that documentation is correctly generated. The `tox` tool can be executed locally to check that local changes won't cause Github Actions Checks to fail.

There are two tox environments available, one for the test cases (`tests`) and one for the framework and libraries (`py3`).

!!! note "Tox Virtual Environment"
    The checks performed by `tox` are sandboxed in their own virtual environments (which are created automatically in the `.tox/` subdirectory). These can be used to debug errors encountered during `tox` execution.

    Whilst we create a virtual environment in the code snippets below, they are only to install the tox tool itself.

## Test Case Verification: `tests`

Prerequisite:
```console
python -m venv ./venv/
source ./venv/bin/activate
pip install tox
```
Verify:
```
tox -e tests
```

## Framework Verification: `py3`

Prerequisite:
```console
python -m venv ./venv/
source ./venv/bin/activate
pip install tox
```
Verify:
```console
tox -e py3
```
