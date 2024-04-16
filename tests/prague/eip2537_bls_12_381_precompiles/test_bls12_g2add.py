"""
abstract: Tests BLS12_G2ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_G2ADD precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Environment
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import StateTestFiller, Transaction

from .helpers import vectors_from_file
from .spec import FORK, PointG2, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from(str(FORK)),
    pytest.mark.parametrize("precompile_address", [Spec.G2ADD], ids=[""]),
]


@pytest.mark.parametrize(
    "input,expected_output",
    vectors_from_file("add_G2_bls.json")
    + [
        pytest.param(
            PointG2(
                (1, 1),
                (
                    0x17FAA6201231304F270B858DAD9462089F2A5B83388E4B10773ABC1EEF6D193B9FCE4E8EA2D9D28E3C3A315AA7DE14CA,  # noqa: E501
                    0xCC12449BE6AC4E7F367E7242250427C4FB4C39325D3164AD397C1837A90F0EA1A534757DF374DD6569345EB41ED76E,  # noqa: E501
                ),
            )
            + PointG2(
                (1, 1),
                (
                    0x17FAA6201231304F270B858DAD9462089F2A5B83388E4B10773ABC1EEF6D193B9FCE4E8EA2D9D28E3C3A315AA7DE14CA,  # noqa: E501
                    0xCC12449BE6AC4E7F367E7242250427C4FB4C39325D3164AD397C1837A90F0EA1A534757DF374DD6569345EB41ED76E,  # noqa: E501
                ),
            ),
            PointG2(
                (
                    0x919F97860ECC3E933E3477FCAC0E2E4FCC35A6E886E935C97511685232456263DEF6665F143CCCCB44C733333331553,  # noqa: E501
                    0x18B4376B50398178FA8D78ED2654B0FFD2A487BE4DBE6B69086E61B283F4E9D58389CCCB8EDC99995718A66666661555,  # noqa: E501
                ),
                (
                    0x26898F699C4B07A405AB4183A10B47F923D1C0FDA1018682DD2CCC88968C1B90D44534D6B9270CF57F8DC6D4891678A,  # noqa: E501
                    0x3270414330EAD5EC92219A03A24DFA059DBCBE610868BE1851CC13DAC447F60B40D41113FD007D3307B19ADD4B0F061,  # noqa: E501
                ),
            ),
            id="not_in_subgroup",
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
    Test the BLS12_G2ADD precompile.
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
    ],
)
@pytest.mark.parametrize("expected_output", [Spec.INVALID], ids=[""])
def test_invalid(
    state_test: StateTestFiller,
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Negative tests for the BLS12_G2ADD precompile.
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
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G2ADD precompile gas requirements.
    """
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
    "input,expected_output",
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
    pre: dict,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_G2ADD precompile using different call types.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
