# EEST Wishlist

This documents a loose collection of ideas for improvements to `ethereum/execution-spec-tests` (EEST).

## TODO Dan

- Review
  - features plugin
  - 7702 test
  - coverage script
- Docs
  - fix nectos/act doc formatting
  - add changelog for uv change
  - update readme/index regarding .venv
  - remove solc-select in readme
- Settings
  - add .venv to vscode settings
- consume:
  - fix pipe bug
  - fix doc bug.

- Doc deprecation warnings are the a subset as those for pytest (they come from running gen_test_case_reference.py).
  - Trie:

    ```console
    ➜ uv add "trie>=3.0.1,<4"
        × No solution found when resolving dependencies for split (python_full_version < '3.13'):
        ╰─▶ Because eth2spec==1.5.0a3 depends on trie==2.0.2 and only eth2spec==1.5.0a3 is available, we can conclude that all versions of eth2spec depend on trie==2.0.2.
            And because ethereum==0.1.0 depends on eth2spec, we can conclude that ethereum==0.1.0 depends on trie==2.0.2.
            And because only ethereum==0.1.0 is available and your project depends on ethereum, we can conclude that your project depends on trie==2.0.2.
            And because your project depends on trie>=3.0.1,<4 and your project requires ethereum-execution-spec-tests[test], we can conclude that your projects's requirements are unsatisfiable.
        help: If this is intentional, run `uv add --frozen` to skip the lock and sync steps.
    ```

    Need to update
        1. Pinned version of trie in eth2spec: https://github.com/ethereum/consensus-specs/blob/dev/setup.py#L556
        2. Pinned version of eth2spec in execution-specs: https://github.com/ethereum/execution-specs/blob/master/setup.cfg#L117
        3. Version range of trie in ethereum-execution-spec-tests: `uv add "trie>=3.0.1,<4`

## Infrastructure

- [ ] Replace `flake8`, `flake8-spellcheck`,  `mypy` and `black` with [`ruff`](https://github.com/astral-sh/ruff) and [`codespell`](https://github.com/codespell-project/codespell). Motivation: `ruff` is insanely fast. For the conversion, it won't be possible to maintain both systems side-by-side, as:
  - [Known deviations from black](https://docs.astral.sh/ruff/formatter/black/).
  - ruff [normalizes hex to lower case](https://github.com/astral-sh/ruff/pull/9280[]) (black doesn't).
  - ruff [forces an additional newline following a module docstring](https://github.com/astral-sh/ruff/pull/8283#issuecomment-2180053177).
- [ ] Separate each test tox environment into `lint` and `test` (to allow for faster linting).
- [x] Use a package manager (`poetry`, `pdm` or `rye`) to manage dependencies (and avoid use of venvs) -> #777
- [ ] Make `execution-spec-tests` an installable package. How to handle the `tests` directory with regards to `cwd`? Currently we assumes is always in the `cwd` where `fill` is executed.
- [ ] Update `mypy` to a newer version.
- [ ] Update `pytest` from 7 to 8.
- [ ] Is there a way to avoid forcing the user to execute `solc-select` after `pip install`?
- [ ] Provide docker images?
- [ ] Clean up `mkdocs build --strict` console log.

- [ ]

## Doc Flow

- Publish pre-release docs..., e.g., `prague-devnet-3@1.4.0`.
- Add a CONTRIBUTING.md file.
- Add a RELEASING.md file.
- Test docstrings as part of `tox -e framework`.
- Add test case documentation to the HTML docs.

## Refactor

- [ ] `ethereum_test_vm`:

    `./tests/` uses (in roughly equal measure):

    1. `from ethereum_test_tools import Opcodes as Op`
    2. `from ethereum_test_tools.vm.opcode import Opcodes as Op`

    Suggestion: Refactor all code to use 1. and remove `from ethereum_test_tools.vm.opcode` that only acts as an alias to `ethereum_test_vm`.

    No tests currently import `ethereum_test_vm` directly. But perhaps they should?

- [ ] Clean-up pytest init files:
  - Move `pytest-framework.ini` to `pyproject.toml`
  - Move all `consume` ini options to `cli` (`-o console_output_style=progress`)
  - Move all `fill` ini options to `cli`?

- [ ] Remove EELS dependencies
  - Use ethereum-types
    - Can we get rlp in ethereum-types?
  - How to handle frontier imports:

    ```
    from ethereum.frontier.fork_types import Account as FrontierAccount
    from ethereum.frontier.fork_types import Address as FrontierAddress
    from ethereum.frontier.state import State, set_account, set_storage,
    ```

## CI/CD

1. Run `-m slow` tests nightly weekly in CI/CD (on all relevant branches).

## `gentest`

1. Add testing in CI/CD (end-to-end: `gentest` -> `fill`).
2. Linting/mypy steps in `tox` must pass on generated output.
3. Add non-legacy transaction support.
4. Coverage checks on framework and framework tests.

## `fill`

1. Don't force `solc` to be installed to fill (non-Yul) tests (just fail them with a warning instead?).

## `consume`

0. Document the `consume` commands.
1. Add `--fork`/`--from`/`--until` command-line arguments to specify fork (ranges), analogous to `fill`'s flags.
2. Add other EVM client `statetest` and `blocktest` implementations to `consume`.
3. Allow `consume rlp`/`consume engine` to be run against a EVM client running locally (non-dockerized). Related: `--rlp-debug-dir`/`--rlp-dump-dir` flag analogous to `--evm-dump-dir` in `fill`.
4. Enable `consume rlp` with `ethereum/tests`.
5. Enable CI/CD testing for `consume` commands.

## Larger Projects

### Extend EEST to allow testing of any EVM implementation

EEST's current focus is Ethereum mainnet. It could be very helpful to the broader community if it was possible to define EVM characteristics and configuration separately and dynamically specify them upon test execution. EVM properties could potentially implemented as a pytest plugin that can be loaded upon request.

The aim would be to achieve a clear separation of concerns between the test framework and the EVM implementation, which would allow EVM teams to use EEST's test cases against their implementation without requiring any changes to the EEST framework or repository.

First attempt (WIP!) here: https://github.com/ethereum/execution-spec-tests/pull/753
