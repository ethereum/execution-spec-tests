"""
abstract: Tests BLS12_G1MSM precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_G1MSM precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Environment, StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import FORK, PointG1, Scalar, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from(str(FORK)),
    pytest.mark.parametrize("precompile_address", [Spec.G1MSM], ids=[""]),
]


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("multiexp_G1_bls.json")
    + [
        pytest.param(
            (Spec.P1 + Scalar(Spec.Q)) * (len(Spec.MSM_DISCOUNT_TABLE) - 1),
            Spec.INF_G1,
            id="max_discount",
        ),
        pytest.param(
            (Spec.P1 + Scalar(Spec.Q)) * len(Spec.MSM_DISCOUNT_TABLE),
            Spec.INF_G1,
            id="max_discount_plus_1",
        ),
    ],
)
def test_msm_g1(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MSM precompile.
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
        pytest.param(
            PointG1(0, 1) + Scalar(0),
            id="invalid_point_1",
        ),
    ],
)
@pytest.mark.parametrize(
    "precompile_gas_modifier", [100_000], ids=[""]
)  # Add gas so that won't be the cause of failure
@pytest.mark.parametrize("expected_output", [b""], ids=[""])
def test_msm_g1_negative(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1MSM precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
