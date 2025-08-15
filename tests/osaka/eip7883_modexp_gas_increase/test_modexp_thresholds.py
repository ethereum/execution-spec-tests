"""
abstract: Tests [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883)
    Test cases for [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883).
"""

from typing import Dict

import pytest

from ethereum_test_checklists import EIPChecklist
from ethereum_test_tools import Alloc, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

from ...byzantium.eip198_modexp_precompile.helpers import ModExpInput
from .helpers import vectors_from_file
from .spec import Spec, ref_spec_7883

REFERENCE_SPEC_GIT_PATH = ref_spec_7883.git_path
REFERENCE_SPEC_VERSION = ref_spec_7883.version

pytestmark = pytest.mark.valid_from("Osaka")


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,gas_old,gas_new",
    vectors_from_file("vectors.json"),
    ids=lambda v: v.name,
)
def test_vectors_from_file(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp gas cost using the test vectors from EIP-7883."""
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,gas_old,gas_new",
    vectors_from_file("legacy.json"),
    ids=lambda v: v.name,
)
def test_vectors_from_legacy_tests(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp gas cost using the test vectors from legacy tests."""
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "modexp_input,",
    [
        # These invalid inputs are from EIP-7823.
        # Ref: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-7823.md#analysis
        pytest.param(
            bytes.fromhex("9e5faafc"),
            id="invalid-case-1",
        ),
        pytest.param(
            bytes.fromhex("85474728"),
            id="invalid-case-2",
        ),
        pytest.param(
            bytes.fromhex("9e281a98" + "00" * 54 + "021e19e0c9bab2400000"),
            id="invalid-case-3",
        ),
    ],
)
@pytest.mark.parametrize(
    "modexp_expected,call_succeeds",
    [
        pytest.param(bytes(), False),
    ],
)
@EIPChecklist.Precompile.Test.Inputs.AllZeros
def test_modexp_invalid_inputs(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp gas cost with invalid inputs."""
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


def create_boundary_modexp_case(
    base: str = "FF", exponent: str = "FF", modulus: str = "FF", case_id: str = ""
):
    """
    Create a single boundary ModExp test case.

    Args:
        base: Base data (hex string)
        exponent: Exponent data (hex string)
        modulus: Modulus data (hex string)
        case_id: Test case identifier

    Returns:
        pytest.param for the test case

    """
    modexp_input = ModExpInput(
        base=base,
        exponent=exponent,
        modulus=modulus,
    )
    return pytest.param(modexp_input, Spec.modexp_error, False, id=case_id)


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,call_succeeds",
    [
        create_boundary_modexp_case(
            base="FF" * (Spec.MAX_LENGTH_BYTES + 1), case_id="base-too-long"
        ),
        create_boundary_modexp_case(
            exponent="FF" * (Spec.MAX_LENGTH_BYTES + 1), case_id="exponent-too-long"
        ),
        create_boundary_modexp_case(
            modulus="FF" * (Spec.MAX_LENGTH_BYTES + 1), case_id="modulus-too-long"
        ),
        create_boundary_modexp_case(
            base="FF" * (Spec.MAX_LENGTH_BYTES + 1),
            exponent="FF",
            modulus="FF" * (Spec.MAX_LENGTH_BYTES + 1),
            case_id="base-modulus-too-long",
        ),
    ],
)
def test_modexp_boundary_inputs(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp boundary inputs."""
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "call_opcode",
    [
        Op.CALL,
        Op.STATICCALL,
        Op.DELEGATECALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "modexp_input,modexp_expected",
    [
        pytest.param(Spec.modexp_input, Spec.modexp_expected, id="base-heavy"),
    ],
)
@EIPChecklist.Precompile.Test.CallContexts.Static
@EIPChecklist.Precompile.Test.CallContexts.Delegate
@EIPChecklist.Precompile.Test.CallContexts.Callcode
@EIPChecklist.Precompile.Test.CallContexts.Normal
def test_modexp_call_operations(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp call related operations with EIP-7883."""
    state_test(
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,precompile_gas_modifier,call_succeeds",
    [
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_expected,
            1,
            True,
            id="extra_gas",
        ),
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_expected,
            0,
            True,
            id="exact_gas",
        ),
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_error,
            -1,
            False,
            id="insufficient_gas",
        ),
    ],
)
@EIPChecklist.Precompile.Test.ValueTransfer.Fee.Over
@EIPChecklist.Precompile.Test.ValueTransfer.Fee.Exact
@EIPChecklist.Precompile.Test.ValueTransfer.Fee.Under
def test_modexp_gas_usage(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp gas cost with different precompile gas modifiers."""
    state_test(pre=pre, tx=tx, post=post)


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,precompile_gas_modifier,call_succeeds",
    [
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_expected,
            1,
            True,
            id="extra_gas",
        ),
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_expected,
            0,
            True,
            id="exact_gas",
        ),
        pytest.param(
            Spec.modexp_input,
            Spec.modexp_error,
            -1,
            False,
            id="insufficient_gas",
        ),
    ],
)
def test_modexp_entry_points(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    modexp_input: bytes,
    tx_gas_limit: int,
):
    """Test ModExp entry points with different precompile gas modifiers."""
    tx = Transaction(
        to=Spec.MODEXP_ADDRESS,
        sender=pre.fund_eoa(),
        data=bytes(modexp_input),
        gas_limit=tx_gas_limit,
    )
    state_test(pre=pre, tx=tx, post={})


def create_modexp_variable_gas_test_cases():
    """
    Create test cases for ModExp variable gas cost testing.

    Returns:
        List of pytest.param objects for the test cases

    """
    # Test case definitions: (base, exponent, modulus, expected_result, test_id)
    test_cases = [
        ("", "", "", "", "Z0"),
        ("01" * 16, "00" * 16, "02" * 16, "00" * 15 + "01", "S0"),
        ("01" * 16, "00" * 15 + "03", "02" * 16, "01" * 16, "S1"),
        ("01" * 32, "FF" * 32, "02" * 32, "01" * 32, "S2"),
        ("01" * 16, "00" * 40, "02" * 16, "00" * 15 + "01", "S3"),
        ("01" * 16, "00" * 39 + "01", "02" * 16, "01" * 16, "S4"),
        ("01" * 24, "00", "02" * 8, "00" * 7 + "01", "S5"),
        ("01" * 8, "01", "02" * 24, "00" * 16 + "01" * 8, "S6"),
        ("01" * 40, "00" * 16, "02" * 40, "00" * 39 + "01", "L0"),
        ("01" * 40, "FF" * 32, "02" * 40, "01" * 40, "L1"),
        ("01" * 40, "00" * 40, "02" * 40, "00" * 39 + "01", "L2"),
        ("01" * 40, "00" * 39 + "01", "02" * 40, "01" * 40, "L3"),
        ("01" * 48, "01", "02" * 16, "01" * 16, "L4"),
        ("01" * 16, "00" * 40, "02" * 48, "00" * 47 + "01", "L5"),
    ]

    # Gas calculation parameters:
    #
    # Please refer to EIP-7883 for details of each function in the gas calculation.
    # Link: https://eips.ethereum.org/EIPS/eip-7883
    #
    # - calculate_multiplication_complexity:
    #   - Comp: if max_length <= 32 bytes, it is Small (S), otherwise it is Large (L)
    #   - Rel (Length Relation): base < modulus (<), base = modulus (=), base > modulus (>)
    #
    # - calculate_iteration_count
    #   - Iter (Iteration Case):
    #     - A: exp≤32 and exp=0
    #     - B: exp≤32 and exp≠0
    #     - C: exp>32 and low256=0
    #     - D: exp>32 and low256≠0
    #
    # - calculate_gas_cost
    #   - Clamp: True if raw gas < 500 (clamped to 500), False if raw gas ≥ 500 (no clamping)

    # Test case coverage table:
    # ┌─────┬──────┬─────┬──────┬───────┬─────────┬─────────────────────────────────────────────┐
    # │ ID  │ Comp │ Rel │ Iter │ Clamp │   Gas   │ Description                                 │
    # ├─────┼──────┼─────┼──────┼───────┼─────────┼─────────────────────────────────────────────┤
    # │ Z0  │  -   │  -  │  -   │  -    │   500   │ Zero case - empty inputs                    │
    # │ S0  │  S   │  =  │  A   │ True  │   500   │ Small, equal, zero exponent, clamped        │
    # │ S1  │  S   │  =  │  B   │ True  │   500   │ Small, equal, small exp, clamped            │
    # │ S2  │  S   │  =  │  B   │ False │  4080   │ Small, equal, large exp, unclamped          │
    # │ S3  │  S   │  =  │  C   │ False │  2032   │ Small, equal, large exp+zero low256         │
    # │ S4  │  S   │  =  │  D   │ False │  2048   │ Small, equal, large exp+non-zero low256     │
    # │ S5  │  S   │  >  │  A   │ True  │   500   │ Small, base>mod, zero exp, clamped          │
    # │ S6  │  S   │  <  │  B   │ True  │   500   │ Small, base<mod, small exp, clamped         │
    # │ L0  │  L   │  =  │  A   │ True  │   500   │ Large, equal, zero exp, clamped             │
    # │ L1  │  L   │  =  │  B   │ False │ 12750   │ Large, equal, large exp, unclamped          │
    # │ L2  │  L   │  =  │  C   │ False │  6350   │ Large, equal, large exp+zero low256         │
    # │ L3  │  L   │  =  │  D   │ False │  6400   │ Large, equal, large exp+non-zero low256     │
    # │ L4  │  L   │  >  │  B   │ True  │   500   │ Large, base>mod, small exp, clamped         │
    # │ L5  │  L   │  <  │  C   │ False │  9144   │ Large, base<mod, large exp+zero low256      │
    # └─────┴──────┴─────┴──────┴───────┴─────────┴─────────────────────────────────────────────┘

    for base, exponent, modulus, expected_result, test_id in test_cases:
        yield pytest.param(
            ModExpInput(base=base, exponent=exponent, modulus=modulus),
            bytes.fromhex(expected_result),
            id=test_id,
        )


@pytest.mark.parametrize(
    "modexp_input,modexp_expected",
    create_modexp_variable_gas_test_cases(),
)
def test_modexp_variable_gas_cost(
    state_test: StateTestFiller,
    pre: Alloc,
    tx: Transaction,
    post: Dict,
):
    """Test ModExp variable gas cost."""
    state_test(pre=pre, tx=tx, post=post)
