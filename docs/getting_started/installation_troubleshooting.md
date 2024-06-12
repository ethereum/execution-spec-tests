# Installation Troubleshooting

This page provides guidance on how to troubleshoot common issues that may arise when installing the Execution Spec Tests repository.

## Pip Installation Issues

### Coincurve Installation

If you encounter an error when installing the `coincurve` package, like the following:

```bash
Stored in directory: /tmp/pip-ephem-wheel-cache-xmvrga07/wheels/8c/b8/07/7845e7297caf68e1436089da2b0e18050e199745a918a7441b
  Building wheel for coincurve (pyproject.toml) ... error
  error: subprocess-exited-with-error
  
  × Building wheel for coincurve (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [27 lines of output]
      ...
      build/temp.linux-x86_64-cpython-312/_libsecp256k1.c:571:10: fatal error: secp256k1_extrakeys.h: No such file or directory
        571 | #include <secp256k1_extrakeys.h>
            |          ^~~~~~~~~~~~~~~~~~~~~~~
      compilation terminated.
      error: command '/usr/bin/gcc' failed with exit code 1
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for coincurve
```

You may need to install the `libsecp256k1` library. On Ubuntu, you can install this library by running the following command:

```bash
sudo apt update
sudo apt-get install libsecp256k1-dev
```
