# Releases

This page provides information about Ethereum Execution Spec Tests (EEST) releases for advanced users who need to work with multiple test fixture sets or understand how EEST releases are structured and managed.

## Types of Releases

EEST provides two main types of releases:

### Full Releases

Full releases are published with version tags following semantic versioning (e.g., `v3.0.0`). These releases contain comprehensive test fixtures for deployed forks and are considered stable for production use.

Full releases typically:
- Are tagged with version numbers like `v3.0.0`, `v3.1.0`, etc.
- Are not marked as "pre-releases" in GitHub
- Contain test fixtures for all stable Ethereum forks
- Undergo thorough testing and review
- Have detailed release notes with a descriptive name (e.g., "Petřín (v3.0.0)")

Full releases are recommended for general use, client compatibility testing, and Continuous Integration (CI) pipelines.

### Pre-releases

Pre-releases are published with feature-specific tags in the format `feature-name@vX.Y.Z` (e.g., `pectra-devnet-5@v1.0.0`, `eip7692@v2.1.0`). These releases contain test fixtures for features under development, devnets, or specific EIPs that haven't been deployed to mainnet yet.

Pre-releases typically:
- Are tagged with feature-specific tags like `feature-name@vX.Y.Z`
- Are marked as "pre-releases" in GitHub
- Focus on specific features, EIPs, or devnets
- May not be as thoroughly tested as full releases
- May contain breaking changes or experimental features
- Have detailed release notes explaining the included EIPs and changes

Pre-releases are invaluable for client teams implementing new features, testing devnets, or working on specific EIPs in parallel.

## Release Naming Conventions

EEST follows these naming conventions for releases:

- **Full releases**: `vX.Y.Z` (e.g., `v3.0.0`)
  - `X`: Major version (breaking changes)
  - `Y`: Minor version (new features, non-breaking)
  - `Z`: Patch version (bug fixes)

- **Pre-releases**: `feature-name@vX.Y.Z` (e.g., `pectra-devnet-5@v1.0.0`)
  - `feature-name`: The name of the feature, devnet, or EIP
  - `vX.Y.Z`: Version number specific to this feature

## Release Process

EEST releases are created automatically through GitHub Actions workflows:

1. For **full releases** (`v3.0.0`), the workflow is triggered when a tag matching the pattern `v[0-9]+.[0-9]+.[0-9]+*` is pushed.

2. For **pre-releases** (`feature-name@vX.Y.Z`), the workflow is triggered when a tag matching the pattern `*@v*` is pushed.

The release process:
1. Builds test fixtures for the specified release
2. Creates a draft release in GitHub
3. Attaches the test fixtures as assets to the release
4. Generates release notes (which can then be edited before publishing)

## Using Releases in EEST

EEST provides several ways to consume release fixtures:

### Command Line

You can use the `consume` command to fetch and use fixtures from a release:

```bash
# Use the latest full release
consume direct --input stable@latest

# Use a specific release version
consume direct --input v3.0.0

# Use a pre-release for a specific feature
consume direct --input pectra-devnet-5@v1.0.0
```

### In Your Code

You can use the `FixturesSource` class to programmatically fetch and use fixtures from a release:

```python
from pytest_plugins.consume.consume import FixturesSource

# Use the latest full release
fixtures = FixturesSource.from_release_spec("stable@latest")

# Use a specific release version
fixtures = FixturesSource.from_release_spec("v3.0.0")

# Use a pre-release for a specific feature
fixtures = FixturesSource.from_release_spec("pectra-devnet-5@v1.0.0")
```

## Release Notes

Release notes are an important part of each release. They typically include:

- The list of included EIPs and their specific versions
- Breaking changes and their impact
- New test formats or changes to existing formats
- Important notes for users of the release

You can find release notes on the [GitHub Releases page](https://github.com/ethereum/execution-spec-tests/releases).

## Documentation Versions

Documentation for each release is also published, allowing you to view the documentation specific to a particular release. You can find the documentation selector in the top-right corner of this page.

Documentation for pre-releases is available at URLs of the form:
`https://eest.ethereum.org/feature-name@vX.Y.Z/`

For example, documentation for the `pectra-devnet-5@v1.0.0` release would be available at:
`https://eest.ethereum.org/pectra-devnet-5@v1.0.0/` 
