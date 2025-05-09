"""
abstract: Tests [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883)
    Test cases for [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883).
"""

from typing import Dict

import pytest

from ethereum_test_tools import (
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)

from . import MODEXP_GAS_INCREASE_FORK_NAME
from .spec import Spec, ref_spec_7883

REFERENCE_SPEC_GIT_PATH = ref_spec_7883.git_path
REFERENCE_SPEC_VERSION = ref_spec_7883.version

pytestmark = pytest.mark.valid_from(MODEXP_GAS_INCREASE_FORK_NAME)


@pytest.mark.parametrize(
    "test_name,base_length,modulus_length,exponent_length,exponent,expected_gas",
    # Spec.TEST_VECTOR_PARAMS,
    # ids=[v[0] for v in Spec.TEST_VECTOR_PARAMS],
    Spec.OLD_TEST_VECTOR_PARAMS,
    ids=[v[0] for v in Spec.OLD_TEST_VECTOR_PARAMS],
)
def test_basic_vectors(
    test_name,
    base_length,
    modulus_length,
    exponent_length,
    exponent,
    expected_gas,
    state_test: StateTestFiller,
    env: Environment,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp gas cost using the test vectors from EIP-7883."""
    state_test(
        env=env,
        pre=pre,
        tx=tx,
        post=post,
    )
