"""
abstract: Tests BLS12_MAP_FP2_TO_G2 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_MAP_FP2_TO_G2 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501


import pytest

from ethereum_test_tools import Environment, StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import FORK, PointG1, PointG2, Scalar, Spec, map_fp_to_g1_format, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from(str(FORK)),
    pytest.mark.parametrize("precompile_address", [Spec.MAP_FP2_TO_G2], ids=[""]),
]


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("map_fp2_to_G2_bls.json"),
)
def test_map_fp2_to_g2(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP2_TO_G2 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
