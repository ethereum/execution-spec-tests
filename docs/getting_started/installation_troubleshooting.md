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

### Problem: `CERTIFICATE_VERIFY_FAILED`

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

### Problem: `Exception: failed to compile yul source`

!!! danger "Problem: `Running fill fails with tests that contain yul source code` on ARM platforms"
    If you're using `x86_64`, try to manually run `solc-select` to install the required version of the `solc` binary:

    ```shell
    uv run solc-select use 0.8.24 --always-install
    ```

    Otherwise, this can happen when you're using an ARM64 OS but followed the x86-64 installation guide.
    To resolve the issue you must build solidity from source (avoid 0.8.24 as it might require building z3 from source as well).

!!! success "Solution: Build solc from source"
    The following steps have been tested on Ubuntu 24.04.2 LTS ARM64:
    ```bash
    git clone --branch v0.8.28 --depth 1 https://github.com/ethereum/solidity.git
    cd solidity && mkdir build && cd build
    sudo apt install build-essential libboost-all-dev z3
    cmake ..
    make
    mv $HOME/Documents/execution-spec-tests/.venv/bin/solc $HOME/Documents/execution-spec-tests/.venv/bin/solc-x86-64
    cp ./solc/solc $HOME/Documents/execution-spec-tests/.venv/bin/
    chmod +x $HOME/Documents/execution-spec-tests/.venv/bin/solc
    ```
    Running `uv run solc --version` should now return the expected version. Verify that `fill` works by running `uv run fill -m yul_test` in the execution-spec-tests root folder.

## Problem: `ValueError: unsupported hash type ripemd160`

!!! danger "Problem: `Running fill fails with tests that use the RIPEMD160 precompile (0x03)`"
    When running `fill`, you encounter the following error:

    ```python
    ValueError: unsupported hash type ripemd160
    # or
    ValueError: [digital envelope routines] unsupported
    ```

    This is due to the removal of certain cryptographic primitives in OpenSSL 3. These were re-introduced in [OpenSSL v3.0.7](https://github.com/openssl/openssl/blob/master/CHANGES.md#changes-between-306-and-307-1-nov-2022).

!!! success "Solution: Modify OpenSSL configuration"
    On platforms where OpenSSL v3.0.7 is unavailable (e.g., Ubuntu 22.04), modify your OpenSSL configuration to enable RIPEMD160. Make the following changes in the OpenSSL config file:

    ```ini
    [openssl_init]
    providers = provider_sect
    
    # List of providers to load
    [provider_sect]
    default = default_sect
    legacy = legacy_sect

    [default_sect]
    activate = 1

    [legacy_sect]
    activate = 1
    ```

    This will enable the legacy cryptographic algorithms, including RIPEMD160. See [ethereum/execution-specs#506](https://github.com/ethereum/execution-specs/issues/506) for more information.

## Other Issues Not Listed?

If you're facing an issue that's not listed here, you can easily report it on GitHub for resolution.

[Click here to report a documentation issue related to installation](https://github.com/ethereum/execution-spec-tests/issues/new?title=docs(bug):%20unable%20to%20install%20eest%20with%20error%20...&labels=scope:docs,type:bug&body=%3Ccopy-paste%20command%20that%20triggered%20the%20issue%20here%3E%0A%3Ccopy-paste%20output%20or%20attach%20screenshot%20here%3E)

Please include the following details in your report:

1. The command that triggered the issue.
2. Any relevant error messages or screenshots.
3. Relevant version information from the output of `uv run eest info` (if running consume from within `eest`).
