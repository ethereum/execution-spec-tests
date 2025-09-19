"""
abstract: Tests [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)
    Test cases for [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)].
"""

import pytest

from ethereum_test_checklists import EIPChecklist
from ethereum_test_tools import (
    Address,
    Alloc,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
    compute_create_address,
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
@EIPChecklist.Precompile.Test.CallContexts.Normal()
@EIPChecklist.Precompile.Test.Inputs.Valid()
@EIPChecklist.Precompile.Test.Inputs.MaxValues()
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
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.Y0 + Spec.X0,
            id="x_and_y_reversed",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Y(Spec.P + 1),
            id="y_greater_than_p",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + X(Spec.P + 1) + Spec.Y0,
            id="x_greater_than_p",
        ),
        pytest.param(
            Spec.H0
            + R(0x813EF79CCEFA9A56F7BA805F0E478584FE5F0DD5F567BC09B5123CCBC9832365)
            + S(0x900E75AD233FCC908509DBFF5922647DB37C21F4AFD3203AE8DC4AE7794B0F87)
            + X(0xB838FF44E5BC177BF21189D0766082FC9D843226887FC9760371100B7EE20A6F)
            + Y(0xF0C9D75BFBA7B31A6BCA1974496EEB56DE357071955D83C4B1BADAA0B21832E9),
            id="valid_secp256k1_inputs",
        ),
        pytest.param(
            H(0x235060CAFE19A407880C272BC3E73600E3A12294F56143ED61929C2FF4525ABB)
            + R(0x182E5CBDF96ACCB859E8EEA1850DE5FF6E430A19D1D9A680ECD5946BBEA8A32B)
            + S(0x76DDFAE6797FA6777CAAB9FA10E75F52E70A4E6CEB117B3C5B2F445D850BD64C)
            + X(0x3828736CDFC4C8696008F71999260329AD8B12287846FEDCEDE3BA1205B12729)
            + Y(0x3E5141734E971A8D55015068D9B3666760F4608A49B11F92E500ACEA647978C7),
            id="wrong_endianness",
        ),
        pytest.param(
            H(Spec.P - 1)
            + R(Spec.N - 2)
            + S((Spec.N - 1) // 2)
            + X(Spec.P - 3)
            + Y(0x19719BEBF6AEA13F25C96DFD7C71F5225D4C8FC09EB5A0AB9F39E9178E55C121),
            id="near_field_boundary_p_minus_3",
        ),
        pytest.param(
            # Invalid curve attack: This point satisfies y² = x³ - 3x + 1 (mod p)
            # instead of the correct P-256 equation y² = x³ - 3x + b where
            # b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
            # This tests that the implementation properly validates the curve equation
            # and rejects points on different curves (CVE-2020-0601 class vulnerability)
            Spec.H0
            + Spec.R0
            + Spec.S0
            + X(0x4)
            + Y(0x872A856D521EED42D28A60CCC2EAE42E1572F33BE2BF616DC9A762D51C459E2A),
            id="invalid_curve_attack_b_equals_one",
        ),
        pytest.param(
            # Invalid curve attack: Singular curve with b = 0
            # Point satisfies y² = x³ - 3x (mod p) - a singular/degenerate curve
            # Singular curves have discriminant = 0 and provide no security guarantees
            # This tests rejection of points on curves with catastrophic security failures
            Spec.H0
            + Spec.R0
            + Spec.S0
            + X(0x2)
            + Y(0x507442007322AA895340CBA4ABC2D730BFD0B16C2C79A46815F8780D2C55A2DD),
            id="invalid_curve_attack_singular_b_zero",
        ),
        pytest.param(
            # Invalid curve attack: Boundary value b = p-1
            # Point satisfies y² = x³ - 3x + (p-1) (mod p)
            # Tests proper parameter validation at modular arithmetic boundaries
            # Ensures implementations handle field arithmetic edge cases correctly
            Spec.H0
            + Spec.R0
            + Spec.S0
            + X(0x1)
            + Y(0x6522AED9EA48F2623B8EEAE3E213B99DA32E74C9421835804D374CE28FCCA662),
            id="invalid_curve_attack_b_equals_p_minus_1",
        ),
        pytest.param(
            # Invalid curve attack: Small discriminant curve with b = 2
            # Point satisfies y² = x³ - 3x + 2 (mod p)
            # Curves with small discriminants are vulnerable to specialized attacks
            # Tests rejection of cryptographically weak curve parameters
            Spec.H0 + Spec.R0 + Spec.S0 + X(0x1) + Y(0x0),
            id="invalid_curve_attack_small_discriminant",
        ),
        pytest.param(
            # Invalid curve attack: Composite order curve with b = 7
            # Point satisfies y² = x³ - 3x + 7 (mod p)
            # Curve order has small factors enabling Pohlig-Hellman attacks
            # Tests protection against small subgroup confinement attacks
            Spec.H0
            + Spec.R0
            + Spec.S0
            + X(0x1)
            + Y(0x85EC5A4AF40176B63189069AEFFCB229C96D3E046E0283ED2F9DAC21B15AD3C),
            id="invalid_curve_attack_composite_order",
        ),
    ],
)
@pytest.mark.parametrize("expected_output", [Spec.INVALID_RETURN_VALUE], ids=[""])
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@EIPChecklist.Precompile.Test.Inputs.AllZeros()
@EIPChecklist.Precompile.Test.Inputs.Invalid()
@EIPChecklist.Precompile.Test.Inputs.Invalid.Crypto()
@EIPChecklist.Precompile.Test.Inputs.Invalid.Corrupted()
@EIPChecklist.Precompile.Test.InputLengths.Zero()
@EIPChecklist.Precompile.Test.InputLengths.Static.Correct()
@EIPChecklist.Precompile.Test.InputLengths.Static.TooShort()
@EIPChecklist.Precompile.Test.InputLengths.Static.TooLong()
@EIPChecklist.Precompile.Test.OutOfBounds.Max()
@EIPChecklist.Precompile.Test.OutOfBounds.MaxPlusOne()
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
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.INVALID_RETURN_VALUE,
            -6900,
            False,
            id="zero_gas",
        ),
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.INVALID_RETURN_VALUE,
            -3450,
            False,
            id="3450_gas",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@EIPChecklist.Precompile.Test.GasUsage.Constant.Exact()
@EIPChecklist.Precompile.Test.GasUsage.Constant.Oog()
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
@EIPChecklist.Precompile.Test.CallContexts.Delegate()
@EIPChecklist.Precompile.Test.CallContexts.Static()
@EIPChecklist.Precompile.Test.CallContexts.Callcode()
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
@EIPChecklist.Precompile.Test.CallContexts.TxEntry()
def test_precompile_as_tx_entry_point(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test P256Verify precompile entry point."""
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,precompile_address,expected_output",
    [
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.P256VERIFY,
            Spec.SUCCESS_RETURN_VALUE,
            id="valid_input_with_value_transfer",
        ),
    ],
)
@EIPChecklist.Precompile.Test.ValueTransfer.NoFee()
def test_precompile_will_return_success_with_tx_value(
    state_test: StateTestFiller,
    pre: Alloc,
    input_data: bytes,
    expected_output: bytes,
    precompile_address: Address,
):
    """Test P256Verify precompile will not fail if value is sent."""
    sender = pre.fund_eoa()
    storage = Storage()

    call_256verify_bytecode = (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
        + Op.CALL(
            gas=Spec.P256VERIFY_GAS,
            address=Spec.P256VERIFY,
            value=Op.CALLVALUE(),
            args_offset=0,
            args_size=Op.CALLDATASIZE(),
            ret_offset=0,
            ret_size=32,
        )
        + Op.SSTORE(storage.store_next(True), Op.DUP1())
        + Op.SSTORE(storage.store_next(expected_output), Op.MLOAD(0))
        + Op.SSTORE(storage.store_next(len(expected_output)), Op.RETURNDATASIZE())
        + Op.STOP
    )

    contract_address = pre.deploy_contract(call_256verify_bytecode)
    tx = Transaction(
        sender=sender,
        gas_limit=1000000,
        to=contract_address,
        value=1000,
        data=input_data,
    )
    post = {contract_address: {"storage": storage}}
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        # Test case where computed x-coordinate exceeds curve order N
        # This tests the modular comparison: r' ≡ r (mod N)
        pytest.param(
            Spec.H0
            # R: A value that when used in ECDSA verification produces an x-coordinate > N
            + R(0x000000000000000000000000000000004319055358E8617B0C46353D039CDAAB)
            + S(0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC63254E)
            # X, Y: Public key coordinates that will produce x-coordinate > N during verification
            + X(0x0AD99500288D466940031D72A9F5445A4D43784640855BF0A69874D2DE5FE103)
            + Y(0xC5011E6EF2C42DCD50D5D3D29F99AE6EBA2C80C9244F4C5422F0979FF0C3BA5E),
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
@EIPChecklist.Precompile.Test.Inputs.Valid()
@EIPChecklist.Precompile.Test.Inputs.Invalid.Crypto()
def test_modular_comparison(state_test: StateTestFiller, pre: Alloc, post: dict, tx: Transaction):
    """
    Test the modular comparison condition for secp256r1 precompile.

    This tests that when the x-coordinate of R' exceeds the curve order N,
    the verification should use modular arithmetic:
    r' ≡ r (mod N) instead of direct equality r' == r.
    """
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.SUCCESS_RETURN_VALUE,
            id="valid_input",
        ),
        pytest.param(
            b"\x00" * 160,
            Spec.INVALID_RETURN_VALUE,
            id="invalid_input",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@EIPChecklist.Precompile.Test.CallContexts.Initcode.Tx()
def test_contract_creation_transaction(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    input_data: bytes,
    expected_output: bytes,
):
    """Test the contract creation for the P256VERIFY precompile."""
    sender = pre.fund_eoa()

    storage = Storage()
    contract_address = compute_create_address(address=sender, nonce=0)
    contract_bytecode = (
        Op.CODECOPY(0, Op.SUB(Op.CODESIZE, len(input_data)), len(input_data))
        + Op.CALL(
            gas=Spec.P256VERIFY_GAS,
            address=Spec.P256VERIFY,
            value=0,
            args_offset=0,
            args_size=len(input_data),
            ret_offset=0,
            ret_size=32,
        )
        + Op.SSTORE(storage.store_next(True), Op.DUP1())
        + Op.SSTORE(storage.store_next(expected_output), Op.MLOAD(0))
        + Op.SSTORE(storage.store_next(len(expected_output)), Op.RETURNDATASIZE())
        + Op.STOP
    )

    tx = Transaction(
        sender=sender,
        gas_limit=1000000,
        to=None,
        value=0,
        data=contract_bytecode + input_data,
    )

    post = {
        contract_address: {
            "storage": storage,
        }
    }
    state_test(env=Environment(), pre=pre, post=post, tx=tx)


@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        pytest.param(
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            Spec.SUCCESS_RETURN_VALUE,
            id="valid_input",
        ),
        pytest.param(
            b"\x00" * 160,
            Spec.INVALID_RETURN_VALUE,
            id="invalid_input",
        ),
    ],
)
@pytest.mark.parametrize("precompile_address", [Spec.P256VERIFY], ids=[""])
@pytest.mark.parametrize("opcode", [Op.CREATE, Op.CREATE2])
@EIPChecklist.Precompile.Test.CallContexts.Initcode.CREATE()
def test_contract_initcode(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    input_data: bytes,
    expected_output: bytes,
    opcode: Op,
):
    """Test P256VERIFY behavior from contract creation."""
    sender = pre.fund_eoa()

    storage = Storage()

    call_256verify_bytecode = (
        Op.CODECOPY(0, Op.SUB(Op.CODESIZE, len(input_data)), len(input_data))
        + Op.CALL(
            gas=Spec.P256VERIFY_GAS,
            address=Spec.P256VERIFY,
            value=0,
            args_offset=0,
            args_size=len(input_data),
            ret_offset=0,
            ret_size=32,
        )
        + Op.SSTORE(storage.store_next(True), Op.DUP1())
        + Op.SSTORE(storage.store_next(expected_output), Op.MLOAD(0))
        + Op.SSTORE(storage.store_next(len(expected_output)), Op.RETURNDATASIZE())
        + Op.STOP
    )
    full_initcode = call_256verify_bytecode + input_data
    total_bytecode_length = len(call_256verify_bytecode) + len(input_data)

    create_contract = (
        Op.CALLDATACOPY(offset=0, size=total_bytecode_length)
        + opcode(offset=0, size=total_bytecode_length)
        + Op.STOP
    )

    factory_contract_address = pre.deploy_contract(code=create_contract)
    contract_address = compute_create_address(
        address=factory_contract_address, nonce=1, initcode=full_initcode, opcode=opcode
    )

    tx = Transaction(
        sender=sender,
        gas_limit=200_000,
        to=factory_contract_address,
        value=0,
        data=call_256verify_bytecode + input_data,
    )

    post = {
        contract_address: {
            "storage": storage,
        }
    }

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
