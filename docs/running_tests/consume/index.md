# The `consume` Command

The EEST `consume` command implements different methods to run EEST-generated test fixtures against clients:

```bash
uv run consume [OPTIONS] SUBCOMMAND [ARGS]...
```

!!! tip "What's difference between `consume engine` and `./hive --sim eest/consume-engine`"

    These commands run the same EEST simulator code, just through different interfaces:

    1. `consume engine` requires the user to [install EEST](../../getting_started/installation.md) and start a Hive server in [development mode](../hive/dev_mode.md). In this case, the simulator is not dockerized. This is particularly useful during test development as fixtures on the local disk can be specified via `--input=fixtures/`.
    2. `./hive --sim eest/consume-engine` is a standalone command that installs the `consume` command in a dockerized container managed by Hive. This is the defacto method for executing EEST [fixture releases](../releases.md) against clients in CI environments. It is cumbersome to execute fixtures on the local disk with this method.

## Available Consumption Methods

Here's a top-level comparison of the different methods of consuming tests:

| Consumed via                                       | Scope       | Pros                                                                                 | Cons                                                                                                                           |
| -------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `statetest` or <code>blocktest</code>-like command | Module test | - Fast feedback loop<br/>- Less complex                                              | - Smaller coverage scope<br/>- Requires a dedicated interface to the client EVM to consume the JSON fixtures and execute tests |
| RLP or Engine Simulator                            | System test | - Tests full client stack<br/>- Real-world code paths<br/>- Comprehensive validation | - Slower than module tests<br/>- More complex setup                                                                            |

!!! top "The `consume` subcommands are pytest-based"

    All `consume` subcommands are based on Python's defacto test framework, [pytest](https://docs.pytest.org/en/8.3.x/index.html). As such, they all take advantage of many pytest test framework features, such as:

    - `-k` test selection via keyword expression.
    - `--collect-only -q`, dry-run; only print collected test (fixture) IDs.
    - `-n 5` run tests across 5 cores using the `pytest-xdist` plugin.
    - `--pdb` drop into a Python debugger.
