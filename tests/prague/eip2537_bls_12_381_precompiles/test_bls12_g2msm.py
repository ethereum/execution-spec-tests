"""
abstract: Tests BLS12_G2MSM precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_G2MSM precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools import Opcodes as Op

from .conftest import G2_POINTS_NOT_IN_SUBGROUP, G2_POINTS_NOT_ON_CURVE
from .helpers import vectors_from_file
from .spec import PointG2, Scalar, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from("Prague"),
    pytest.mark.parametrize("precompile_address", [Spec.G2MSM], ids=[""]),
]


@pytest.mark.parametrize(
    "input_data,expected_output,vector_gas_value",
    # Test vectors from the reference spec (from the cryptography team)
    vectors_from_file("msm_G2_bls.json")
    + [
        # Single pair scalar multiplication cases.
        pytest.param(
            Spec.INF_G2 + Scalar(0),
            Spec.INF_G2,
            None,
            id="single_inf_times_zero",
        ),
        pytest.param(
            Spec.INF_G2 + Scalar(1),
            Spec.INF_G2,
            None,
            id="single_inf_times_one",
        ),
        pytest.param(
            Spec.G2 + Scalar(0),
            Spec.INF_G2,
            None,
            id="single_generator_times_zero",
        ),
        pytest.param(
            Spec.G2 + Scalar(1),
            Spec.G2,
            None,
            id="single_generator_times_one",
        ),
        pytest.param(
            Spec.P2 + Scalar(Spec.Q),
            Spec.INF_G2,
            None,
            id="single_point_times_q",
        ),
        pytest.param(
            Spec.P2 + Scalar(2**256 - 1),
            PointG2(
                (
                    0x2663E1C3431E174CA80E5A84489569462E13B52DA27E7720AF5567941603475F1F9BC0102E13B92A0A21D96B94E9B22,  # noqa: E501
                    0x6A80D056486365020A6B53E2680B2D72D8A93561FC2F72B960936BB16F509C1A39C4E4174A7C9219E3D7EF130317C05,  # noqa: E501
                ),
                (
                    0xC49EAD39E9EB7E36E8BC25824299661D5B6D0E200BBC527ECCB946134726BF5DBD861E8E6EC946260B82ED26AFE15FB,  # noqa: E501
                    0x5397DAD1357CF8333189821B737172B18099ECF7EE8BDB4B3F05EBCCDF40E1782A6C71436D5ACE0843D7F361CBC6DB2,  # noqa: E501
                ),
            ),
            None,
            id="single_point_times_max_scalar",
        ),
        # Multiple pair scalar multiplication cases.
        pytest.param(
            Spec.G2 + Scalar(1) + Spec.INF_G2 + Scalar(1),
            Spec.G2,
            None,
            id="g2_plus_inf",
        ),
        pytest.param(
            Spec.G2 + Scalar(0) + Spec.P2 + Scalar(0) + Spec.INF_G2 + Scalar(0),
            Spec.INF_G2,
            None,
            id="all_zero_scalars",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + (-Spec.G2) + Scalar(1),
            Spec.INF_G2,
            None,
            id="sum_to_identity_opposite",
        ),
        pytest.param(
            Spec.G2 + Scalar(Spec.Q - 1) + Spec.G2 + Scalar(1),
            Spec.INF_G2,
            None,
            id="scalars_sum_to_q",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + Spec.G2 + Scalar(0) + Spec.INF_G2 + Scalar(5),
            Spec.G2,
            None,
            id="combined_basic_cases",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + Spec.INF_G2 + Scalar(500),
            Spec.G2,
            None,
            id="identity_with_large_scalar",
        ),
        pytest.param(
            Spec.G2 + Scalar(0) + Spec.P2 + Scalar(0) + (-Spec.G2) + Scalar(0),
            Spec.INF_G2,
            None,
            id="multiple_points_zero_scalar",
        ),
        # Cases with maximum discount table (test vector for gas cost calculation)
        pytest.param(
            (Spec.P2 + Scalar(Spec.Q)) * (len(Spec.G2MSM_DISCOUNT_TABLE) - 1),
            Spec.INF_G2,
            None,
            id="max_discount",
            marks=pytest.mark.slow,
        ),
        pytest.param(
            (Spec.P2 + Scalar(Spec.Q)) * len(Spec.G2MSM_DISCOUNT_TABLE),
            Spec.INF_G2,
            None,
            id="max_discount_plus_1",
            marks=pytest.mark.slow,
        ),
    ],
)
def test_valid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test valid calls to the BLS12_G2MSM precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input_data",
    # Test vectors from the reference spec (from the cryptography team)
    vectors_from_file("fail-msm_G2_bls.json")
    + [
        pytest.param(
            PointG2((1, 0), (0, 0)) + Scalar(0),
            id="invalid_point_a_1",
        ),
        pytest.param(
            PointG2((0, 1), (0, 0)) + Scalar(0),
            id="invalid_point_a_2",
        ),
        pytest.param(
            PointG2((0, 0), (1, 0)) + Scalar(0),
            id="invalid_point_a_3",
        ),
        pytest.param(
            PointG2((0, 0), (0, 1)) + Scalar(0),
            id="invalid_point_a_4",
        ),
        pytest.param(
            PointG2((Spec.P, 0), (0, 0)) + Scalar(0),
            id="x_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, Spec.P), (0, 0)) + Scalar(0),
            id="x_2_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (Spec.P, 0)) + Scalar(0),
            id="y_1_equal_to_p",
        ),
        pytest.param(
            PointG2((0, 0), (0, Spec.P)) + Scalar(0),
            id="y_2_equal_to_p",
        ),
        pytest.param(
            b"\x80" + bytes(Spec.INF_G2)[1:] + Scalar(0),
            id="invalid_encoding",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP + Scalar(1),
            id="not_in_subgroup_1",
        ),
        pytest.param(
            Spec.P2_NOT_IN_SUBGROUP_TIMES_2 + Scalar(1),
            id="not_in_subgroup_2",
        ),
        pytest.param(
            G2_POINTS_NOT_IN_SUBGROUP[0] + Scalar(0),
            id="rand_not_in_subgroup_0",
        ),
        pytest.param(
            G2_POINTS_NOT_IN_SUBGROUP[1] + Scalar(1),
            id="rand_not_in_subgroup_1",
        ),
        pytest.param(
            G2_POINTS_NOT_ON_CURVE[0] + Scalar(0),
            id="not_on_curve_0",
        ),
        pytest.param(
            G2_POINTS_NOT_ON_CURVE[1] + Scalar(1),
            id="not_on_curve_1",
        ),
        pytest.param(
            Spec.G2,
            id="bls_g2_truncated_input",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + Spec.G2,
            id="incomplete_input_missing_scalar",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + bytes([0]),
            id="incomplete_input_extra_byte",
        ),
        pytest.param(
            Spec.G2 + Scalar(1) + Spec.G1 + Scalar(1),
            id="mixing_g2_with_g1",
        ),
        pytest.param(
            Spec.G2 + (b"\x01" + b"\x00" * 32),  # Scalar > UINT256_MAX
            id="scalar_too_large",
        ),
        pytest.param(
            Spec.G2 + Scalar(1).x.to_bytes(16, byteorder="big"),  # Invalid scalar length
            id="scalar_too_short",
        ),
        pytest.param(
            bytes([0]) * 287,  # Just under minimum valid length
            id="input_too_short_by_1",
        ),
    ],
    # Input length tests can be found in ./test_bls12_variable_length_input_contracts.py
)
@pytest.mark.parametrize(
    "precompile_gas_modifier", [100_000], ids=[""]
)  # Add gas so that won't be the cause of failure
@pytest.mark.parametrize("expected_output", [Spec.INVALID], ids=[""])
def test_invalid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test invalid calls to the BLS12_G2MSM precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "call_opcode",  # Note `Op.CALL` is used for all the `test_valid` cases.
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
            Spec.INF_G2 + Scalar(0),
            Spec.INF_G2,
            id="single_inf_times_zero",
        ),
        pytest.param(
            Spec.G2 + Scalar(0) + Spec.INF_G2 + Scalar(0),
            Spec.INF_G2,
            id="msm_all_zeros_different_call_types",
        ),
    ],
)
def test_call_types(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_G2MSM precompile using different call types."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
