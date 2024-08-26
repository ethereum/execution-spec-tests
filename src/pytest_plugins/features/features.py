"""
Enable feature-specific functionality during test filling/execution.
"""
from enum import Flag, auto

import pytest

from ethereum_test_vm import EVMCodeType


class Features(Flag):
    """
    Enumerates the available features.
    """

    NONE = 0
    EIP_7702 = auto()
    EOF_V1 = auto()

    def __str__(self):
        """
        Returns the string representation of the feature.
        """
        return self.name


def pytest_addoption(parser: pytest.Parser):
    """
    Adds command-line options to pytest.
    """
    features_group = parser.getgroup(
        "features", "Arguments related to enabling specific testing of features"
    )

    features_group.addoption(
        "--feature",
        action="append",
        default=[],
        help="Enable a feature (repeat for multiple features). Supported features: "
        + ", ".join(str(feature).lower() for feature in Features),
    )


@pytest.fixture(scope="session")
def features(request):
    """
    Returns the enabled features.
    """
    features_str_list = request.config.getoption("feature")
    features = Features.NONE
    for feature_str in features_str_list:
        features |= Features[feature_str.upper()]
    return features


@pytest.fixture(scope="session")
def eip_7702_feature(features: Features) -> bool:
    """
    Returns whether the EIP-7702 mode is enabled.
    """
    return Features.EIP_7702 in features


@pytest.fixture(autouse=True, scope="session")
def evm_code_type(features: Features) -> EVMCodeType | None:
    """
    Returns the default EVM code type for all tests.
    """
    if Features.EOF_V1 in features:
        return EVMCodeType.EOF_V1
    return None
