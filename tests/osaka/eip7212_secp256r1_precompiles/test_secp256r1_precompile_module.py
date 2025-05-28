"""
abstract: Tests [EIP-7212 EIP-7212: Precompiled for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7212)
    Test cases for [EIP-7212 EIP-7212: Precompiled for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7212)].
"""

import pytest

from ethereum_test_tools import Alloc, Environment, StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import Spec, ref_spec_7212

REFERENCE_SPEC_GIT_PATH = ref_spec_7212.git_path
REFERENCE_SPEC_VERSION = ref_spec_7212.version

pytestmark = [
    pytest.mark.valid_from("Osaka"),
    pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""]),
]


@pytest.mark.parametrize(
    "input_data,expected_output,vector_gas_value",
    vectors_from_file("secp256r1_test.json"),
)
def test_valid(state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction):
    """Test P256Verify precompile."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)
