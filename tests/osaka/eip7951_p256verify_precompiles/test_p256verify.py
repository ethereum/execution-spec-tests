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
        pytest.param(
            # Invalid curve attack: Composite order curve with b = -Spec.B
            # Random point which satisfies y² = x³ - 3x - Spec.B (mod p)
            # Without the curve check in the implementation, the signature checks out.
            H(0xC223E1538C4D7B5BBD3EF932736826FD64F4E8B5C80250D9E07A728689D13C38)
            + R(0x0C7CB59EF6BE7539397CC979AD9A87A3B73A0DD268BBA4990A3378C6391512D5)
            + S(0xF8C943685BCFE7864C0F8485CACD732D3A9F167531CAF26B67A3CB10B641F92C)
            + X(0xF1F2ADE681DB5699741B1F9FF080E9A08DCFF48F48A5048C4D90EC89440C3EFB)
            + Y(0xBFFE372E7BBDBD60E4DF885E17A37878461AE13B6491E7863020305962F2C6B6),
            id="invalid_curve_attack_bneg_1",
        ),
        pytest.param(
            # Invalid curve attack: Composite order curve with b = -Spec.B
            # Random point which satisfies y² = x³ - 3x - Spec.B (mod p)
            # Without the curve check in the implementation, the signature checks out.
            H(0x982D25BF8E0E81FF41AC3C8033604C78ED5EF17C6EDDA977072EAB6821A7AD0A)
            + R(0x7C1996FA0EC911E4739AE7340B5345823272F494DFA32034A4FE5642C3DB91F2)
            + S(0x1E4D6CCF1AFB675D18BD27274770C8B84028D272D1D2641E70B30E1DF17AF3DC)
            + X(0xC9124B6AB12F08790A2712AEC74A1B71FA997CA7DE1E9117BC18D07DCBFE7C91)
            + Y(0xADD1E9DF40A47ADD6B2191C05D0C1B4AF1BAEEAA0C0A97E7B3D06FFAE543D096),
            id="invalid_curve_attack_bneg_2",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0)
            + R(0xD21697149F598FEAE9A750DCA86AE6D5EFA654680BA748D2DF7053115101C129)
            + S(0xEF3FD943AD1F126B3EBA1A5900D79886755DB6DAFCB6B0117D86364340CE36CC)
            + X(0x687216395BD2F58E5A6D91964AE67E766DF2A2FB8E623795A5852507927C70C2)
            + Y(0xF40E19B93BEB5C0678EDE25AB3654E08C0C6EF6A143CEC9865F3A447C6EB84E3),
            id="invalid_curve_attack_h0_random1",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0)
            + R(0x52E47C5D6AAB66AB6A18A694359EB86FDD40F10E79EF5493C5469EC88BA03334)
            + S(0x7584C5BF3CA2869C7E383B1603A935EEB79D990B7F7152E055EC562E87FD715E)
            + X(0x0000000000000002000000000000000000000000000000000000000000000000)
            + Y(0x000000000000000000000000000000000000000000000000FE00000000000000),
            id="invalid_curve_attack_h0_random2",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0)
            + R(0x81333B13B13F362253BD536D17563A72EB575F1993F55ED40E633E503F60B864)
            + S(0xE2208C4045F5241ECCF08F825399224C4B78595A10433EC33799DCAD7B0E1F4A)
            + X(0xCE9C1088B4BCC71223A187410BB05819A6D32D2F1A1024B83557E51833AB23DC)
            + Y(0x00FB64209538D1143A88E8B91D2DA46095AF852D7DD494BE6AF26C29D545F856),
            id="invalid_curve_attack_h0_random3",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0)
            + R(0x3C593B5857D1D0EB83923D73E76A7A53EF191BB210267D8C0BE17A4E34AB2E73)
            + S(0xD022359310067882F713AFBECECE71CB80E4857368F46AB0346362DB033ED298)
            + X(0x358DF65C0D732CCAB431D4CAB7F98E9F9279BD71D64635FAB21EA87EF254C5D1)
            + Y(0x82909FF2E230433D000000000000000000000000000000000000000000000000),
            id="invalid_curve_attack_h0_random4",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0)
            + R(0x425CFFCA652791CABFC81B1E4B7712DBA196599FABCE16978E06E6AF486B1FEC)
            + S(0x58B864B5A41CD17524E4773EC353C9590D792F601DA075AD9B3F40E8E7070E8A)
            + X(0x00000000000000000000000000000000000000000000000000007FFFFFFFFFFF)
            + Y(0xFFFF000000000000000000000000000000000000000000000000000000000000),
            id="invalid_curve_attack_h0_random5",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0x2DA0A74BE3122AEAEF5704D0EB27881FBFB918B4A5252B660935263D0569BA92)
            + R(0x5543729CBCFD99EE6C3B422D7F245903E7177B3A6A4E3C20C0DC5F5E109795AE)
            + S(0x96403D5BB253EBD7DEF44BCBC062FCD4EA5E358B19B67C13E625EFDF6B977597)
            + X(0x996CADC001622FB5E363B421A08854096569397B3BDCB8C3DEC907392F7CC59B)
            + Y(0xD34A4E0F08C6FC549F7FAFFBCAF610D7F6C467B7B27072720E81079FB6595B52),
            id="invalid_curve_attack_random6",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0x1F9D9B26DB42380C85F075174DDAF158F9DE4CD10C3104190D7AF96938DD8ECD)
            + R(0x159946DBC4F1DE68CD4096862A5B10E5986ACB32229D6E68884DC83DAB70A307)
            + S(0x63D80724A4074421F7DD255630794E3AEBE635B756D72B24652AAC07D01B289C)
            + X(0x9CA2F39CC3536861000000000000000000000000000000000000000000000000)
            + Y(0x000000000000B100000000000000000000000000000000000000000000000000),
            id="invalid_curve_attack_random7",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0xD380DA9251F1FB809ED48C70DC8F81E91C471F0E81BC95E7611C653278A5B6B4)
            + R(0xFF197EB72A9E531B17B872525247E6564B786CC014ED28B6849CE7D8C976BDF2)
            + S(0x7B0B2EFF9BB5409052B35FD3FF81DCE77D95A1F75C46989817045120DA5C3C9C)
            + X(0xBA7695481956A6269DD646ADDD4AFE6D9763637D76AD780299E51201384A8403)
            + Y(0xA62443DD4AFE6D9763637D76AD780299E51201384AE4FEDD3CDAC9F461600D53),
            id="invalid_curve_attack_random8",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0x4B082B60497ED87FFE570612D521E73A2CD6C832744EF8E4E2E329E30D3D5879)
            + R(0x6665A88CB3FF30D339A1975FD46CF5EF480A68A093AB778550073D3528C3B609)
            + S(0xAEAADDB235E4AC6097356DB96161E27849EA8EDF1E971F74EB51E19A1CC950A1)
            + X(0x0000000000000002000000000000000000000000000000000000000000000000)
            + Y(0x000000000000000000000000000000000000000000000000FE00000000000000),
            id="invalid_curve_attack_random9",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0x6CC2B605CFBDB22B9E7B55EFE8C1DA0F1C5A0EC1AA8D82EEDFB5EA70E9846E88)
            + R(0x3C593B5857D1D0EB83923D73E76A7A53EF191BB210267D8C0BE17A4E34AB2E73)
            + S(0xD022359310067882F713AFBECECE71CB80E4857368F46AB0346362DB033ED298)
            + X(0x358DF65C0D732CCAB431D4CAB7F98E9F9279BD71D64635FAB21EA87EF254C5D1)
            + Y(0x82909FF2E230433D000000000000000000000000000000000000000000000000),
            id="invalid_curve_attack_random10",
        ),
        pytest.param(
            # Invalid curve attack: random point bytes.
            # Without the curve check in the implementation, the signature checks out.
            H(0x810C1D53EA96A700C93F6AF1C183197B040EA6FEAE10564877A1C78EC6074FF1)
            + R(0x34D0F0C8E14D39002B5DEA00808957963E849503DDFD626323433047D696C7C4)
            + S(0x6A7FE39C046304317F799FB900877073F2AE3C798DD4414795551A833ABCBA85)
            + X(0x0000000000F90000000067923073C067015B601D94F262F0E82B9DA2D33A6A32)
            + Y(0xFC3D71CB490CF346ED31DC37405FB0069F4A7ED188381DC049ABAB66E9F80080),
            id="invalid_curve_attack_random_11",
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
