# VS Code Setup

VS Code setup is optional, but does offer the following advantages:

- Auto-format your Python code to conform to the repository's [code standards](../writing_tests/code_standards.md) ([ruff](https://docs.astral.sh/ruff/)).
- Inline linting and auto-completion (thanks to Python type hints).
- Spell-check your code and docs.
- Graphical exploration of test cases and easy test execution/debug.

## Installation

Please refer to the [Visual Studio Code docs](https://code.visualstudio.com/docs/setup/setup-overview) for help with installation.

## VS Code Settings file

The [ethereum/execution-spec-tests](https://github.com/ethereum/execution-spec-tests) repo includes configuration files for VS Code in the `.vscode/` sub-directory:

```text
📁 execution-test-specs/
└──📁 .vscode/
    ├── 📄 settings.json
    ├── 📄 settings.local.recommended.json
    ├── 📄 extensions.json
    └── 📄 launch.recommended.json
```

By default the repository settings are applied via `.vscode/settings.json`, if you want to add your own settings please edit `.vscode/settings.local.recommended.json`.

To enable the recommended launch configurations:

```console
cp .vscode/launch.recommended.json .vscode/launch.json
```

To additionally use and add local settings please run the following first:

```console
cp .vscode/settings.local.recommended.json .vscode/settings.local.json
```

## Additional VS Code Extensions

Open the folder in VS Code where execution-spec-tests is cloned: VS Code should prompt to install the repository's required extensions from `.vscode/extensions.json`:

- [`ms-python.python`](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [`charliermarsh.ruff`](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [`esbenp.prettier-vscode`](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
- [`streetsidesoftware.code-spell-checker`](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
- [`tamasfe.even-better-toml`](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)

!!! note "Workspace Trust"
Trust the `execution-specs-test` repository when opening in VS Code to be prompted to install the plugins recommended via the `extensions.json` file.

The `.vscode/extensions.json` additionally contains a list of extensions that should be disabled:

- [`ms-python.isort`](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)
- [`ms-python.flake8`](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8)
- [`ms-python.black-formatter`](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)

Please ensure that these are disabled for the repo if they are installed as part of your VS Code extensions.

## Configuration for Testing EVM Features Under Active Development

An additional step is required to enable fixture generations for features from forks that are under active development and have not been deployed to mainnet, see [Filling Tests for Features under Development](../filling_tests/filling_tests_dev_fork.md#vs-code-setup).
