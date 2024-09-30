# Running Github Actions Locally

The Github Actions workflows can be tested locally using [nektos/act](https://github.com/nektos/act) without pushing changes to the remote. The local repository state will be used in the executed workflow.

## Prerequisites

1. Install the Github CLI (`gh`): [linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md), [macos](https://github.com/cli/cli/tree/trunk?tab=readme-ov-file#macos).
2. Install the `act` tool as a Github extension ([nektos/act docs](https://nektosact.com/installation/gh.html)):

    ```bash
    gh extension install https://github.com/nektos/gh-act
    ```

    or use one of the [other available methods](https://nektosact.com/installation/index.html).

3. Authenticate your Github account with the Github CLI:

    ```bash
    gh auth login
    ```

    This is required to set `GITHUB_TOKEN` to the output of `gh auth token` when running the workflows.

!!! note "Updating nektos/act to the latest version via the Github CLI"
    The `act` tool can be updated via the Github CLI:

    ```bash
    gh extension upgrade nektos/act
    ```

## Listing the Available Workflows

```bash
gh act list
```

will output something similar to:

```bash
INFO[0000] Using docker host 'unix:///var/run/docker.sock', and daemon socket 'unix:///var/run/docker.sock' 
Stage  Job ID                Job name              Workflow name                             Workflow file          Events                             
0      evmone-coverage-diff  evmone-coverage-diff  Evmone Coverage Report                    coverage.yaml          pull_request                       
0      deploy                deploy                Deploy Docs Main                          docs_main.yaml         push                               
0      deploy                deploy                Deploy Docs Tags                          docs_tags.yaml         push                               
0      features              features              Build and Package Fixtures                fixtures.yaml          push,workflow_dispatch             
0      feature-names         feature-names         Build and Package Fixtures for a feature  fixtures_feature.yaml  push,workflow_dispatch             
0      build                 build                 Run Tox Verifications                     tox_verify.yaml        push,pull_request,workflow_dispatch
1      build                 build                 Build and Package Fixtures                fixtures.yaml          push,workflow_dispatch             
1      build                 build                 Build and Package Fixtures for a feature  fixtures_feature.yaml  push,workflow_dispatch             
2      release               release               Build and Package Fixtures                fixtures.yaml          push,workflow_dispatch             
2      release               release               Build and Package Fixtures for a feature  fixtures_feature.yaml  push,workflow_dispatch
```

The `Job ID` is required to run a specific workflow and is provided to the `-j` option of `gh act`.

## Running Workflows Locally

!!! note "Specifying the `ubuntu-24.04` docker image"

    [#792](https://github.com/ethereum/execution-spec-tests/pull/792/) made EELS the default `t8n` tool. Our Github workflows were changed to use the `ubuntu-24.04` docker image which has OpenSSL 3.0.7, required by EELs to have RIPEMD160 support (used by the precompile at `0x03`). As of 2024-09-30 `ubuntu-latest` resolves to `ubuntu-22-04`.
    
    To run workflows that use `ubuntu-24.04` with `act` (as of version 0.2.67) the following must be added to the command-line:

    ```bash
    -P ubuntu-24.04=ghcr.io/catthehacker/ubuntu:full-24.04
    ```

    See also [Installation Troubleshooting](../getting_started/installation_troubleshooting.md#problem-valueerror-unsupported-hash-type-ripemd160) for more information.

### Running Workflows Locally that use a Matrix Strategy

```bash
gh act -j build --workflows .github/workflows/tox_verify.yaml -s GITHUB_TOKEN=$(gh auth token) --matrix python:3.10 -P ubuntu-24.04=ghcr.io/catthehacker/ubuntu:full-24.04
```

### Running Release Workflows

Release builds require the `ref` input to be specified. To test a release build locally:

1. Create a JSON file specifying the input data required for a release build (the release tag), e.g, `event.json`:

    ```json
    {
        "ref": "refs/tags/stable@v4.2.0"
    }
    ```

2. Run `act` and specify the workflow file, the Github token, and the event file:

    ```bash
    gh act -j build --workflows .github/workflows/fixtures_feature.yaml -s GITHUB_TOKEN=$(gh auth token) -e event.json -P ubuntu-24.04=ghcr.io/catthehacker/ubuntu:full-24.04
    ```
