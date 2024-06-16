"""
A pytest plugin that verifies that the spec, client and test versions match.

Try this plugin using the demo test module (demo/test_1559.py), for example
with "normal" mode:

```
fill --eip-versions-spec \
    src/pytest_plugins/eip_versioning/tests/resources/eip_versions_spec.json \
    --eip-versions-client \
    src/pytest_plugins/eip_versioning/tests/resources/eip_versions_client.json \
    --fork=Cancun --eip-version-mode=normal -m state_test \
    demo/test_1559.py
```
"""

# TODO: Add pydantic models for EIP versions (keys must start "EIP-", values must be semver)


import argparse
import json
import warnings
from enum import Enum
from pathlib import Path

import pytest
import semver


class EipVersionModes(Enum):
    """
    Enum for EIP versioning modes.
    """

    OFF = "off"
    NORMAL = "normal"
    STRICT = "strict"


def pytest_addoption(parser):
    """
    Add pytest cli options.
    """
    eip_versioning = parser.getgroup("eip_ver", "Arguments related to EIP version checks")

    version_modes = ", ".join([mode.value for mode in EipVersionModes])

    def eip_version_mode_type(value):
        try:
            return EipVersionModes(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"Invalid value for EipVersionModes: {value}. Must be one of: {version_modes}."
            )

    eip_versioning.addoption(
        "--eip-version-mode",
        action="store",
        dest="eip_version_mode",
        type=eip_version_mode_type,
        choices=list(EipVersionModes),
        default=EipVersionModes.OFF,
        help=(
            f"Specify the mode for EIP version checks ({version_modes}). "
            "'off': No version checks are performed. "
            "'normal': xfail/xpass the test upon mismatching major versions. "
            "'strict': fail the test upon mismatching major versions. "
        ),
    )
    eip_versioning.addoption(
        "--eip-versions-spec",
        action="store",
        dest="eip_versions_spec",
        type=Path,
        default=None,
        help=(
            "[DEBUG ONLY] Path to a json file defining EIPs and their current versions as "
            "according to the spec (ethereum/EIPs)."
        ),
    )
    eip_versioning.addoption(
        "--eip-versions-client",
        action="store",
        dest="eip_versions_client",
        type=Path,
        default=None,
        help=(
            "[DEBUG ONLY] Path to a json file defining EIPs and their current versions as "
            "implemented in the client binary used in this test session."
        ),
    )


def pytest_configure(config):
    """
    Configuration for EIP versioning. Retrieve the EIP versions from the:
    - latest spec definition (ethereum/EIPs),
    - client binary configured for this test session.
    """
    config.addinivalue_line(
        "markers",
        "eip_version_test(eip, version): mark test as implementing an EIP at a specific version.",
    )

    if config.getoption("eip_version_mode") == EipVersionModes.OFF:
        return
    if config.getoption("eip_version_mode") in ["normal", "strict"]:
        if not config.getoption("eip_versions_client"):
            pytest.exit("EIP version checks require --eip-versions-client to be set.")
        if not config.getoption("eip_versions_spec"):
            pytest.exit("EIP version checks require --eip-versions-spec to be set.")

    config.eip_versions_client = None
    if config.getoption("eip_versions_client"):
        if not config.option.eip_versions_client.exists():
            pytest.exit(
                f"Client versions file {config.option.eip_versions_client} does not exist."
            )
        with open(config.option.eip_versions_client, "r") as f:
            data = json.load(f)
            if "eip_versions" not in data:
                pytest.exit(
                    "Client versions file {config.option.eip_versions_client} does not contain a "
                    "top-level dict with key 'eip_versions'."
                )
            config.eip_versions_client = data["eip_versions"]
    else:
        pass  # TODO: Retrieve the EIP versions supported from the client binary

    config.eip_versions_spec = None
    if config.getoption("eip_versions_spec"):
        if not config.option.eip_versions_spec.exists():
            pytest.exit(f"Spec versions file {config.option.eip_versions_spec} does not exist.")
        with open(config.option.eip_versions_spec, "r") as f:
            data = json.load(f)
            if "eip_versions" not in data:
                pytest.exit(
                    "Spec versions file {config.option.eip_versions_spec} does not contain a "
                    "top-level dict with key 'eip_versions'."
                )
            config.eip_versions_spec = data["eip_versions"]
    else:
        pass  # TODO: Retrieve the EIP versions from ethereum/EIPs


def pytest_collection_modifyitems(config, items):
    """
    Apply markers or issue warnings upon incompatible EIP versions.

    - Apply xfail if test and client major versions differ.
    - Warn if EIP is not reported by client or spec.
    """
    eip_version_mode = config.getoption("eip_version_mode")
    if eip_version_mode == EipVersionModes.OFF:
        return
    for item in items:
        for marker in item.iter_markers(name="eip_version_test"):
            eip = marker.args[0]
            version_test = semver.Version.parse(marker.args[1])
            version_client = config.eip_versions_client.get(eip, None)
            version_spec = config.eip_versions_spec.get(eip, None)

            if version_client is None:
                warnings.warn(
                    f"Test implements {eip} v{version_test} but EIP not reported by client binary."
                )
            else:
                version_client = semver.Version.parse(version_client)
                if (
                    eip_version_mode == EipVersionModes.NORMAL
                    and version_test.major != version_client.major
                ):
                    item.add_marker(
                        pytest.mark.xfail(
                            run=True,
                            reason=(
                                f"Test implements {eip}, v{version_test}; "
                                f"client reports v{version_client}."
                            ),
                        )
                    )

            if version_spec is None:
                warnings.warn(
                    f"Test implements {eip} v{version_test} but EIP not reported by ethereum/EIPs."
                )
            else:
                version_spec = semver.Version.parse(version_spec)


def pytest_runtest_call(item):
    """
    Fail the test as following if we're running in strict mode:

    1. EIP version is not reported by client.
    2. Test and client major versions differ.
    """
    if item.config.getoption("eip_version_mode") != EipVersionModes.STRICT:
        return
    for marker in item.iter_markers(name="eip_version_test"):
        # TODO: If multiple markers for the same EIP are present, e.g., once on the module and once
        # on the function level, all will be checked. However,only the closest one should be
        # checked. This is left as-is for now to check all eip_version_test with different EIP
        # numbers. Can item.get_closest_marker("eip_version_test") be used on a argument value
        # (EIP number) basis?

        eip = marker.args[0]
        version_test = semver.Version.parse(marker.args[1])
        version_client = item.config.eip_versions_client.get(eip, None)
        if version_client is None:
            pytest.fail(
                f"Test implements {eip} v{version_test} but EIP not reported by client binary."
            )
        version_client = semver.Version.parse(version_client)
        if version_test.major != version_client.major:
            pytest.fail(
                f"Test implements {eip} v{version_test} but client reports v{version_client}.",
                pytrace=False,
            )
