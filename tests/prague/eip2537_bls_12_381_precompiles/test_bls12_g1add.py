"""
abstract: Tests BLS12_G1ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_G1ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Environment, StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import FORK, PointG1, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from(str(FORK)),
    pytest.mark.parametrize("precompile_address", [Spec.G1ADD], ids=[""]),
]


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("add_G1_bls.json")
    + [
        pytest.param(
            Spec.INF_G1 + Spec.INF_G1,
            Spec.INF_G1,
            id="inf_plus_inf",
        ),
    ],
)
def test_valid(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1ADD precompile.
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
            PointG1(0, 1) + Spec.INF_G1,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y - 1) + Spec.INF_G1,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y + 1) + Spec.INF_G1,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.x) + Spec.INF_G1,
            id="invalid_point_a_4",
        ),
        pytest.param(
            PointG1(Spec.P1.x, Spec.P1.y - 1) + Spec.P1,
            id="invalid_point_a_5",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(0, 1),
            id="invalid_point_b_1",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.y - 1),
            id="invalid_point_b_2",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.y + 1),
            id="invalid_point_b_3",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x),
            id="invalid_point_b_4",
        ),
        pytest.param(
            Spec.P1 + PointG1(Spec.P1.x, Spec.P1.y - 1),
            id="invalid_point_b_5",
        ),
        pytest.param(
            PointG1(Spec.P, 0) + Spec.INF_G1,
            id="a_x_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(Spec.P, 0),
            id="b_x_equal_to_p",
        ),
        pytest.param(
            PointG1(0, Spec.P) + Spec.INF_G1,
            id="a_y_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G1 + PointG1(0, Spec.P),
            id="b_y_equal_to_p",
        ),
        pytest.param(
            (Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x))[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G1 + PointG1(Spec.P1.x, Spec.P1.x)),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
        ),
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
    Negative tests for the BLS12_G1ADD precompile.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input,expected_output,precompile_gas_modifier",
    [
        pytest.param(
            Spec.INF_G1 + Spec.INF_G1,
            Spec.INF_G1,
            1,
            id="extra_gas",
        ),
        pytest.param(
            Spec.INF_G1 + Spec.INF_G1,
            b"",
            -1,
            id="insufficient_gas",
        ),
    ],
)
def test_gas(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G1ADD precompile gas consumption.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
