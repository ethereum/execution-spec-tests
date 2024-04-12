"""
abstract: Tests BLS12_MAP_FP_TO_G1 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_MAP_FP_TO_G1 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501


import pytest

from ethereum_test_tools import Environment, StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import FORK, Spec, map_fp_to_g1_format, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from(str(FORK)),
    pytest.mark.parametrize("precompile_address", [Spec.MAP_FP_TO_G1], ids=[""]),
]


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("map_fp_to_G1_bls.json"),
)
def test_valid(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP_TO_G1 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input",
    [
        pytest.param(map_fp_to_g1_format(0)[1:], id="input_too_short"),
        pytest.param(b"\x00" + map_fp_to_g1_format(0), id="input_too_long"),
        pytest.param(b"", id="zero_lenght_input"),
        pytest.param(map_fp_to_g1_format(Spec.P), id="fq_eq_q"),
        pytest.param(map_fp_to_g1_format(2**381), id="fq_eq_2_381"),
        pytest.param(map_fp_to_g1_format(2**381 - 1), id="fq_eq_2_381_minus_1"),
        pytest.param(map_fp_to_g1_format(2**382), id="fq_eq_2_382"),
        pytest.param(map_fp_to_g1_format(2**382 - 1), id="fq_eq_2_382_minus_1"),
        pytest.param(map_fp_to_g1_format(2**383), id="fq_eq_2_383"),
        pytest.param(map_fp_to_g1_format(2**383 - 1), id="fq_eq_2_383_minus_1"),
        pytest.param(map_fp_to_g1_format(2**512 - 1), id="fq_eq_2_512_minus_1"),
    ],
)
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
def test_invalid(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP_TO_G1 precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
