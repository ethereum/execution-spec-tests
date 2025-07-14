+++
title = 'Filling Tests for Features under Development'
+++

## Requirements

By default, execution-spec-tests only generates fixtures for forks that have been deployed to mainnet. In order to generate fixtures for evm features that are actively under development:

1. A version of the `evm` and `solc` tools that implement the feature must be available (although, typically only a developer version of the `evm` tool is required, usually the latest stable release of `solc` is adequate), and,
2. The development fork to test must be explicitly specified on the command-line:

{{< tabs >}}

{{< tab "via the `--fork` flag" >}}
```console
uv run fill -k 4844 --fork=Cancun -v
```
{{< /tab >}}

{{< tab "via the `--from` flag" >}}
```console
uv run fill -k 4844 --from=Cancun -v
```
{{< /tab >}}

{{< tab "via the `--until` flag" >}}
```console
uv run fill -k 4844 --until=Cancun -v
```
{{< /tab >}}

{{< /tabs >}}


{{< callout info "Specifying the `evm` binary via `evm-bin`" >}}
It is possible to explicitly specify the `evm` binary used to generate fixtures via the `--evm-bin` flag, for example,

```console
uv run fill --fork=Cancun --evm-bin=/opt/bin/evm -v
```
{{< /callout >}}

## Further Help

1. [`geth`/`evm` build documentation](https://geth.ethereum.org/docs/getting-started/installing-geth#build-from-source).
2. [`solc` build documentation](https://docs.soliditylang.org/en/v0.8.20/installing-solidity.html#building-from-source).

{{< callout info "Verifying `evm` and `solc` versions used" >}}
The versions used to generate fixtures are displayed in the console output:
![Screenshot of pytest test collection console output](/images/filling_tests/pytest_run_example.png)
{{< /callout >}}

## VS Code Setup

By default, VS Code's Testing View will only show tests for stable forks. To show tests for development forks, uncomment the relevant line in the `python.testing.pytestArgs` configuration section of included settings file (`.vscode/settings.json`) to enable the `--until=FORK` flag. See [VS Code Setup](../getting_started/setup_vs_code.md) for help finding the settings files.
