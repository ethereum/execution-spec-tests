"""
abstract: Tests [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)
    Test cases for [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)].
"""

import pytest

from ethereum_test_tools import (
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op

from .helpers import vectors_from_file
from .spec import H, R, S, Spec, X, Y, ref_spec_7951

REFERENCE_SPEC_GIT_PATH = ref_spec_7951.git_path
REFERENCE_SPEC_VERSION = ref_spec_7951.version

pytestmark = [
    pytest.mark.valid_from("Osaka"),
]


@pytest.mark.parametrize(
    "input_data,expected_output,vector_gas_value",
    vectors_from_file("secp256r1_test.json"),
    # Test vectors generated from Wycheproof's ECDSA secp256r1 SHA-256 test suite
    # Source: https://github.com/C2SP/wycheproof/blob/main/testvectors/ecdsa_secp256r1_sha256_test.json
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.eip_checklist("precompile/test/call_contexts/normal")
@pytest.mark.eip_checklist("precompile/test/inputs/valid")
def test_valid(state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction):
    """Test P256Verify precompile."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data",
    [
        pytest.param(b"", id="zero_length_input"),
        pytest.param(
            b"\x00" + Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            id="input_too_long",
        ),
        pytest.param(
            (Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0)[:-1],
            id="input_too_short",
        ),
        pytest.param(
            H(0) + R(0) + S(0) + X(0) + Y(0),
            id="input_all_zeros",
        ),
        pytest.param(
            Spec.H0 + R(0) + Spec.S0 + Spec.X0 + Spec.Y0,
            id="r_eq_to_zero",
        ),
        pytest.param(
            Spec.H0 + R(Spec.N) + Spec.S0 + Spec.X0 + Spec.Y0,
            id="r_eq_to_n",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + S(0) + Spec.X0 + Spec.Y0,
            id="s_eq_to_zero",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + S(Spec.N) + Spec.X0 + Spec.Y0,
            id="s_eq_to_n",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + X(Spec.P) + Spec.Y0,
            id="x_eq_to_p",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Y(Spec.P),
            id="y_eq_to_p",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + X(0) + Y(0),
            id="point_on_infinity",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + X(Spec.X0.value + 1) + Spec.Y0,
            id="point_not_on_curve_x",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Y(Spec.Y0.value + 1),
            id="point_not_on_curve_y",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [Spec.INVALID_RETURN_VALUE], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.eip_checklist("precompile/test/inputs/all_zeros")
@pytest.mark.eip_checklist("precompile/test/inputs/invalid")
@pytest.mark.eip_checklist("precompile/test/inputs/invalid/crypto")
@pytest.mark.eip_checklist("precompile/test/inputs/invalid/corrupted")
@pytest.mark.eip_checklist("precompile/test/input_lengths/static/correct")
@pytest.mark.eip_checklist("precompile/test/input_lengths/static/too_short")
@pytest.mark.eip_checklist("precompile/test/input_lengths/static/too_long")
def test_invalid(state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction):
    """Negative tests for the P256VERIFY precompile."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,expected_output,precompile_gas_modifier,call_succeeds",
    [
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.SUCCESS_RETURN_VALUE,
            1,
            True,
            id="extra_gas",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.INVALID_RETURN_VALUE,
            -1,
            False,
            id="insufficient_gas",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.eip_checklist("precompile/test/gas_usage/constant/exact")
@pytest.mark.eip_checklist("precompile/test/gas_usage/constant/oog")
def test_gas(state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction):
    """Test P256Verify precompile gas requirements."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


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
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.SUCCESS_RETURN_VALUE,
            id="valid_call",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.eip_checklist("precompile/test/call_contexts/delegate")
@pytest.mark.eip_checklist("precompile/test/call_contexts/static")
@pytest.mark.eip_checklist("precompile/test/call_contexts/callcode")
def test_call_types(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test P256Verify precompile using different call types."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,call_contract_address,post",
    [
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.P256VERIFY,
            {},
            id="valid_entry_point",
        ),
    ],
)
@pytest.mark.eip_checklist("precompile/test/call_contexts/tx_entry")
def test_precompile_as_tx_entry_point(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test P256Verify precompile entry point."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        # Test case where computed x-coordinate exceeds curve order N
        # This tests the modular comparison: r' ≡ r (mod N)
        pytest.param(
            H(0xBB5A52F42F9C9261ED4361F59422A1E30036E7C32B270C8807A419FECA605023)
            # R: A value that when used in ECDSA verification produces an x-coordinate > N
            + R(0x2BA3A8BE6B94D5EC80A6D9D1190A436EFFE50D85A1EEE859B8CC6AF9BD5C2E18)
            + S(0x4CD60B855D442F5B3C7B11EB6C4E0AE7525FE710FAB9AA7C77A67F79E6FADD76)
            # X, Y: Public key coordinates that will produce x-coordinate > N during verification
            + X(0x2927B10512BAE3EDDCFE467828128BAD2903269919F7086069C8C4DF6C732838)
            + Y(0xC7787964EAAC00E5921FB1498A60F4606766B3D9685001558D1A974E7341513E),
            Spec.SUCCESS_RETURN_VALUE,
            id="modular_comparison_x_coordinate_exceeds_n",
        ),
        pytest.param(
            Spec.H0
            + R(Spec.N + 1)  # R = N + 1 ≡ 1 (mod N)
            + Spec.S0
            + Spec.X0
            + Spec.Y0,
            Spec.INVALID_RETURN_VALUE,  # Should fail because R = 1 is not a valid signature
            id="r_equals_n_plus_one",
        ),
        pytest.param(
            Spec.H0
            + R(Spec.N + 2)  # R = N + 2 ≡ 2 (mod N)
            + Spec.S0
            + Spec.X0
            + Spec.Y0,
            Spec.INVALID_RETURN_VALUE,  # Should fail because R = 2 is not a valid signature
            id="r_equals_n_plus_two",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.eip_checklist("precompile/test/inputs/valid")
@pytest.mark.eip_checklist("precompile/test/inputs/invalid/crypto")
def test_modular_comparison(
    state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction
):
    """
    Test the modular comparison condition for secp256r1 precompile.

    This tests that when the x-coordinate of R' exceeds the curve order N,
    the verification should use modular arithmetic:
    r' ≡ r (mod N) instead of direct equality r' == r.
    """
    state_test(env=Environment(), pre=pre, post=post, tx=tx)
