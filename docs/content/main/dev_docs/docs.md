# Documentation

The `execution-spec-tests` documentation is generated via [`hugo`](https://github.com/gohugoio/hugo) and hosted remotely on Github Pages at [eest.ethereum.org](https://eest.ethereum.org/).

## Prerequisites

Grab the latest `hugo` binary from the official release page or build it yourself. Then make the binary executable and add it to the PATH (or to a directory that has already been added to the PATH like e.g. `/usr/local/bin/`). We do not require any additional plugins or dependencies.

## Build and Locally Host the Documentation

Build the docs:

```console
hugo
```

If you want to build + locally host the docs:

```console
hugo server
```

## Remote Deployment and Versioning

The execution-specs-test docs are hosted using Github pages at [eest.ethereum.org](https://eest.ethereum.org/). Versions are updated/deployed automatically as part of Github Actions.

### CI/CD: Doc Deployment via Github Actions

This is our workflow that automatically deploys updated/new versions of the docs:

| Workflow `yaml` File | What | When |
|----------------------|------|------|
| `docs.yaml`     | Deploy new version of docs
