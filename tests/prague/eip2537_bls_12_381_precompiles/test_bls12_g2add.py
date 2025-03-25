"""
abstract: Tests BLS12_G2ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_G2ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools import Opcodes as Op

from .helpers import add_points_g2, vectors_from_file
from .spec import PointG2, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from("Prague"),
    pytest.mark.parametrize("precompile_address", [Spec.G2ADD], ids=[""]),
]


@pytest.mark.parametrize(
    "input_data,expected_output,vector_gas_value",
    # Test vectors from the reference spec (from the cryptography team)
    vectors_from_file("add_G2_bls.json")
    + [
        # Identity (infinity) element test cases.
        # Checks that any point added to the identity element (INF) equals itself.
        pytest.param(
            Spec.G2 + Spec.INF_G2,
            Spec.G2,
            None,
            id="generator_plus_inf",
        ),
        pytest.param(
            Spec.INF_G2 + Spec.G2,
            Spec.G2,
            None,
            id="inf_plus_generator",
        ),
        pytest.param(
            Spec.INF_G2 + Spec.INF_G2,
            Spec.INF_G2,
            None,
            id="inf_plus_inf",
        ),
        pytest.param(
            Spec.INF_G2 + Spec.P2,
            Spec.P2,
            None,
            id="inf_plus_point",
        ),
        # Basic arithmetic properties test cases.
        # Checks fundamental properties of the BLS12-381 curve.
        pytest.param(
            Spec.P2 + (-Spec.P2),
            Spec.INF_G2,
            None,
            id="point_plus_neg_point",
        ),
        pytest.param(
            Spec.G2 + (-Spec.G2),
            Spec.INF_G2,
            None,
            id="generator_plus_neg_point",
        ),
        pytest.param(
            Spec.P2 + Spec.G2,
            add_points_g2(Spec.G2, Spec.P2),
            None,
            id="commutative_check_a",
        ),
        pytest.param(
            Spec.G2 + Spec.P2,
            add_points_g2(Spec.P2, Spec.G2),
            None,
            id="commutative_check_b",
        ),
        pytest.param(
            Spec.P2 + Spec.P2,
            add_points_g2(Spec.P2, Spec.P2),
            None,
            id="point_doubling",
        ),
        pytest.param(  # (P + G) + P = P + (G + P)
            add_points_g2(Spec.P2, Spec.G2) + Spec.P2,
            add_points_g2(Spec.P2, add_points_g2(Spec.G2, Spec.P2)),
            None,
            id="associativity_check",
        ),
        pytest.param(  # -(P+G) = (-P)+(-G)
            (-(add_points_g2(Spec.P2, Spec.G2))) + Spec.INF_G2,
            add_points_g2((-Spec.P2), (-Spec.G2)),
            None,
            id="negation_of_sum",
        ),
        pytest.param(
            add_points_g2(Spec.G2, Spec.G2) + add_points_g2(Spec.P2, Spec.P2),
            add_points_g2(add_points_g2(Spec.G2, Spec.G2), add_points_g2(Spec.P2, Spec.P2)),
            None,
            id="double_generator_plus_double_point",
        ),
        pytest.param(
            add_points_g2(Spec.G2, Spec.G2) + add_points_g2(Spec.G2, Spec.G2),
            add_points_g2(add_points_g2(Spec.G2, Spec.G2), add_points_g2(Spec.G2, Spec.G2)),
            None,
            id="double_generator_plus_double_generator",
        ),
        pytest.param(  # (x,y) + (x,-y) = INF
            PointG2(Spec.P2.x, Spec.P2.y)
            + PointG2(Spec.P2.x, (-Spec.P2.y[0] % Spec.P, -Spec.P2.y[1] % Spec.P)),
            Spec.INF_G2,
            None,
            id="point_plus_reflected_point",
        ),
        # Not in the r-order subgroup test cases.
        # Checks that any point on the curve but not in the subgroup is used for operations.
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP + Spec.P2_NOT_IN_SUBGROUP,
            Spec.P2_NOT_IN_SUBGROUP_TIMES_2,
            None,
            id="non_sub_plus_non_sub",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP + Spec.P2_NOT_IN_SUBGROUP_TIMES_2,
            add_points_g2(Spec.P2_NOT_IN_SUBGROUP, Spec.P2_NOT_IN_SUBGROUP_TIMES_2),
            None,
            id="non_sub_plus_doubled_non_sub",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP + Spec.INF_G2,
            Spec.P2_NOT_IN_SUBGROUP,
            None,
            id="non_sub_plus_inf",
        ),
        pytest.param(
            Spec.G2 + Spec.P2_NOT_IN_SUBGROUP,
            add_points_g2(Spec.G2, Spec.P2_NOT_IN_SUBGROUP),
            None,
            id="generator_plus_non_sub",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP + (-Spec.P2_NOT_IN_SUBGROUP),
            Spec.INF_G2,
            None,
            id="non_sub_plus_neg_non_sub",
        ),
        pytest.param(
            Spec.P2 + Spec.P2_NOT_IN_SUBGROUP,
            add_points_g2(Spec.P2, Spec.P2_NOT_IN_SUBGROUP),
            None,
            id="in_sub_plus_non_sub",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP_TIMES_2 + Spec.P2,
            add_points_g2(Spec.P2_NOT_IN_SUBGROUP_TIMES_2, Spec.P2),
            None,
            id="doubled_non_sub_plus_in_sub",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP_TIMES_2 + (-Spec.P2_NOT_IN_SUBGROUP),
            Spec.P2_NOT_IN_SUBGROUP,
            None,
            id="doubled_non_sub_plus_neg",
        ),
        # Boundary point test cases. TODO: requires generated points
        # pytest.param(
        # G2_POINT_NEAR_P + Spec.INF_G2,
        # G2_POINT_NEAR_P,
        # None,
        # id="near_p_boundary_plus_inf",
        # ),
        # pytest.param(
        # G2_POINT_NEAR_ZERO + Spec.INF_G2,
        # G2_POINT_NEAR_ZERO,
        # None,
        # id="near_zero_boundary_plus_inf",
        # ),
        # pytest.param(
        # G2_POINT_NEAR_ZERO + G2_POINT_NEAR_P,
        # add_points_g2(G2_POINT_NEAR_ZERO, G2_POINT_NEAR_P),
        # None,
        # id="near_zero_boundary_plus_near_p_boundary",
        # ),
        # pytest.param(
        # G2_POINT_NEAR_P + G2_POINT_NEAR_P,
        # add_points_g2(G2_POINT_NEAR_P, G2_POINT_NEAR_P),
        # None,
        # id="doubling_near_p_boundary",
        # ),
        # pytest.param(
        # Spec.G2 + G2_POINT_NEAR_P + G2_POINT_NEAR_ZERO,
        # add_points_g2(add_points_g2(Spec.G2, G2_POINT_NEAR_P), G2_POINT_NEAR_ZERO),
        # None,
        # id="chained_boundary_points",
        # ),
        # pytest.param(
        # G2_POINT_NEAR_P + PointG2(G2_POINT_NEAR_P.x, Spec.P - G2_POINT_NEAR_P.y),
        # Spec.INF_G2,
        # None,
        # id="near_p_boundary_plus_its_neg",
        # ),
    ],
)
def test_valid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_G2ADD precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input_data",
    vectors_from_file("fail-add_G2_bls.json")
    + [
        pytest.param(
            PointG2((1, 0), (0, 0)) + Spec.INF_G2,
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG2((0, 0), (1, 0)) + Spec.INF_G2,
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG2((0, 1), (0, 0)) + Spec.INF_G2,
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG2((0, 0), (0, 1)) + Spec.INF_G2,
            id="invalid_point_a_4",
        ),
        pytest.param(
            PointG2(Spec.P2.x, (Spec.P2.y[0], Spec.P2.y[1] - 1)) + Spec.P2,
            id="invalid_point_a_5",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((1, 0), (0, 0)),
            id="invalid_point_b_1",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (1, 0)),
            id="invalid_point_b_2",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 1), (0, 0)),
            id="invalid_point_b_3",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (0, 1)),
            id="invalid_point_b_4",
        ),
        pytest.param(
            Spec.P2 + PointG2(Spec.P2.x, (Spec.P2.y[0], Spec.P2.y[1] - 1)),
            id="invalid_point_b_5",
        ),
        pytest.param(
            PointG2((Spec.P, 0), (0, 0)) + Spec.INF_G2,
            id="a_x_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, Spec.P), (0, 0)) + Spec.INF_G2,
            id="a_x_2_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (Spec.P, 0)) + Spec.INF_G2,
            id="a_y_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (0, Spec.P)) + Spec.INF_G2,
            id="a_y_2_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((Spec.P, 0), (0, 0)),
            id="b_x_1_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, Spec.P), (0, 0)),
            id="b_x_2_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (Spec.P, 0)),
            id="b_y_1_equal_to_p",
        ),
        pytest.param(
            Spec.INF_G2 + PointG2((0, 0), (0, Spec.P)),
            id="b_y_2_equal_to_p",
        ),
        pytest.param(
            b"\x80" + bytes(Spec.INF_G2)[1:] + Spec.INF_G2,
            id="invalid_encoding_a",
        ),
        pytest.param(
            Spec.INF_G2 + b"\x80" + bytes(Spec.INF_G2)[1:],
            id="invalid_encoding_b",
        ),
        pytest.param(
            (Spec.INF_G2 + Spec.INF_G2)[:-1],
            id="input_too_short",
        ),
        pytest.param(
            b"\x00" + (Spec.INF_G2 + Spec.INF_G2),
            id="input_too_long",
        ),
        pytest.param(
            b"",
            id="zero_length_input",
        ),
        pytest.param(
            Spec.G2,
            id="only_one_point",
        ),
        pytest.param(
            PointG2((Spec.P + 1, 0), (0, 0)) + Spec.INF_G2,
            id="x1_above_modulus",
        ),
        pytest.param(
            PointG2(
                (0x01, 0),  # x coordinate in Fp2 (1 + 0i)
                (0x07, 0),  # y coordinate satisfying y^2 = x^3 + 5 in Fp2
            )
            + Spec.INF_G2,
            id="point_on_wrong_curve_b=5",
        ),
        pytest.param(
            bytes(Spec.G2) + bytes(Spec.G2)[128:],
            id="mixed_g1_g2_points",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [Spec.INVALID], ids=[""])
def test_invalid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Negative tests for the BLS12_G2ADD precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input_data,expected_output,precompile_gas_modifier",
    [
        pytest.param(
            Spec.INF_G2 + Spec.INF_G2,
            Spec.INF_G2,
            1,
            id="extra_gas",
        ),
        pytest.param(
            Spec.INF_G2 + Spec.INF_G2,
            Spec.INVALID,
            -1,
            id="insufficient_gas",
        ),
    ],
)
def test_gas(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_G2ADD precompile gas requirements."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "call_opcode",
    [
        Op.STATICCALL,
        Op.DELEGATECALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        pytest.param(
            Spec.INF_G2 + Spec.INF_G2,
            Spec.INF_G2,
            id="inf_plus_inf",
        ),
    ],
)
def test_call_types(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_G2ADD precompile using different call types."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
