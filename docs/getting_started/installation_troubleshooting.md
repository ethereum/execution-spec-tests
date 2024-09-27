# Installation Troubleshooting

This page provides guidance on how to troubleshoot common issues that may arise when installing [ethereum/execution-spec-tests](https://github.com/ethereum/execution-spec-tests).

## Problem: `Failed building wheel for coincurve`

!!! danger "Problem: `Failed building wheel for coincurve`"
    Installing EEST and its dependencies via `uv sync --all-extras` fails with:

    ```bash
    Stored in directory: /tmp/...
      Building wheel for coincurve (pyproject.toml) ... error
      error: subprocess-exited-with-error
      
      × Building wheel for coincurve (pyproject.toml) did not run successfully.
      │ exit code: 1
      ╰─> [27 lines of output]
          ...
            571 | #include <secp256k1_extrakeys.h>
                |          ^~~~~~~~~~~~~~~~~~~~~~~
          compilation terminated.
          error: command '/usr/bin/gcc' failed with exit code 1
          [end of output]
      
      note: This error originates from a subprocess, and is likely not a problem with pip.
      ERROR: Failed building wheel for coincurve
    ```

!!! success "Solution: Install the `libsecp256k1` library"
    On Ubuntu, you can install this library with:

    ```bash
    sudo apt update
    sudo apt-get install libsecp256k1-dev
    ```

## Problem: `solc` Installation issues

!!! danger "Problem: `Failed to install solc ... CERTIFICATE_VERIFY_FAILED`"
    When running either `uv run solc-select use 0.8.24 --always-install` or `fill` you encounter the following error:

    ```bash
    Exit: Failed to install solc version 0.8.24: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:992)>
    ```

=== "Ubuntu"

    !!! success "Solution: Update your system’s CA certificates"
        On Ubuntu, run the following commands:

        ```bash
        sudo apt-get update
        sudo apt-get install ca-certificates
        ```

=== "macOS"

    !!! success "Solution: Update your system’s CA certificates"
        On macOS, Python provides a built-in script to install the required certificates:

        ```bash
        /Applications/Python\ 3.11/Install\ Certificates.command
        ```

## Other Issues Not Listed?

If you're facing an issue that's not listed here, you can easily report it on GitHub for resolution.

[Click here to report a documentation issue related to installation](https://github.com/ethereum/execution-spec-tests/issues/new?title=docs(bug):%20unable%20to%20install%20eest%20with%20error%20...&labels=scope:docs,type:bug&body=%3Ccopy-paste%20command%20that%20triggered%20the%20issue%20here%3E%0A%3Ccopy-paste%20output%20or%20attach%20screenshot%20here%3E)

Please include the following details in your report:

1. The command that triggered the issue.
2. Any relevant error messages or screenshots.
