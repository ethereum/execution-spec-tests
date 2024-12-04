"""
abstract: Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
    Tests uncoupled blob txs for [EIP-7742: Uncouple blob count between CL and EL](https://eips.ethereum.org/EIPS/eip-7742)
"""  # noqa: E501

import pytest

from ethereum_test_tools import Alloc, Environment, StateTestFiller, Transaction

from .spec import Spec, ref_spec_7742

REFERENCE_SPEC_GIT_PATH = ref_spec_7742.git_path
REFERENCE_SPEC_VERSION = ref_spec_7742.version


@pytest.mark.parametrize(
    "blobs_per_tx",
    [(0,)],
)
@pytest.mark.valid_from("Prague")
def test_zero_blobs_in_blob_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test that a blob transaction with zero blobs is accepted in Prague (EIP-7742).
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )


@pytest.mark.parametrize(
    "blobs_per_tx",
    [
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 1,),
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 2,),
        (Spec.CANCUN_MAX_BLOBS_PER_BLOCK + 3,),
    ],
)
@pytest.mark.valid_from("Prague")
def test_blobs_above_cancun_max(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test that transactions with blob counts above the Cancun maximum are accepted in Prague.
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )


@pytest.mark.parametrize(
    "blobs_per_tx",
    [(i,) for i in range(64, 1024, 64)],
)
@pytest.mark.valid_from("Prague")
def test_large_number_of_blobs_in_tx(
    state_test: StateTestFiller,
    pre: Alloc,
    state_env: Environment,
    txs: list[Transaction],
):
    """
    Test transactions with a large number of blobs (64 to 1024 blobs).
    """
    state_test(
        pre=pre,
        post={},
        tx=txs[0],
        env=state_env,
    )
