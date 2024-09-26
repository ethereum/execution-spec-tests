# Testing Github Actions Locally

The Github Actions workflows can be tested locally using [nektos/act](https://github.com/nektos/act) which allows you to test Github Actions locally, without pushing changes to the remote.

## Prerequisites

1. Install the `act` tool, [docs](https://nektosact.com/installation/index.html).
2. Install the Github CLI (`gh`) for authentication: [linux](https://github.com/cli/cli/blob/trunk/docs/install_linux.md), [macos](https://github.com/cli/cli/tree/trunk?tab=readme-ov-file#macos).
3. Authenticate with the Github CLI:

    ```bash
    gh auth login
    ```

## Testing Workflows

### Testing a Workflow that uses a Matrix Strategy

```bash
act -j build --workflows .github/workflows/tox_verify.yaml -s GITHUB_TOKEN=$(gh auth token) --matrix python:3.10
```

### Testing Release Builds

Release builds require the `ref` input to be specified. To test a release build locally:

1. Create a JSON file specifying the input data required for a release build (the release tag), e.g, `event.json`:

    ```json
    {
        "ref": "refs/tags/stable@v4.2.0"
    }
    ```

2. Run `act` and specify the workflow file, the Github token, and the event file:

    ```bash
    act -j build --workflows .github/workflows/fixtures_feature.yaml -s GITHUB_TOKEN=$(gh auth token) -e event.json
    ```
