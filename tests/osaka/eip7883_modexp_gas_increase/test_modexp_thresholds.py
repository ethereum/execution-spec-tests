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
from .helpers import vectors_from_file
from .spec import ref_spec_7883

REFERENCE_SPEC_GIT_PATH = ref_spec_7883.git_path
REFERENCE_SPEC_VERSION = ref_spec_7883.version

pytestmark = pytest.mark.valid_from(MODEXP_GAS_INCREASE_FORK_NAME)


@pytest.mark.parametrize("input_data,expected_gas", vectors_from_file("vectors.json"))
def test_vectors_from_file(
    expected_gas: int,
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
