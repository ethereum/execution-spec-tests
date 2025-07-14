+++
title = 'Consume'
date = 2025-07-09T12:42:33Z
draft = false
[menus]
  [menus.main]
    parent = 'Running Tests'

+++

# The `consume` Command

The EEST `consume` command implements different methods to run EEST-generated test fixtures against clients:

```bash
uv run consume [OPTIONS] SUBCOMMAND [ARGS]...
```

For help with installation, see [Installation](../../getting_started/main.md).

This section provides help for running the EEST commands directly (as opposed to running as a `./hive` [standalone command](../hive/main.md), where applicable) see:

1. [Consume Cache & Fixture Inputs](./cache.md) for how to specify `consume` fixture input.

2. [Consume Direct](./direct.md) to run test fixtures against direct client interfaces.

3. [Consume Simulators](./simulators.md) for help with Hive Simulators.
