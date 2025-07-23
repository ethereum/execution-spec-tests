"""
abstract: Tests [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883)
    Test cases for [EIP-7883: ModExp Gas Cost Increase](https://eips.ethereum.org/EIPS/eip-7883).
"""

from typing import Dict

import pytest

from ethereum_test_checklists import EIPChecklist
from ethereum_test_tools import (
    Alloc,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import vectors_from_file
from .spec import Spec, ref_spec_7883

REFERENCE_SPEC_GIT_PATH = ref_spec_7883.git_path
REFERENCE_SPEC_VERSION = ref_spec_7883.version

pytestmark = pytest.mark.valid_from("Prague")


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


def create_modexp_input(
    bsize: int, esize: int, msize: int, e_data: str = "", m_data: str = "", b_data: str = ""
) -> bytes:
    """
    Create ModExp input data with specified sizes and data.

    Args:
        bsize: Base size in bytes
        esize: Exponent size in bytes
        msize: Modulus size in bytes
        e_data: Exponent data (hex string, if not provided, will be padded with FF)
        m_data: Modulus data (hex string, if not provided, will be padded with FF)
        b_data: Base data (hex string, if not provided, will be padded with FF)

    Returns:
        ModExp input as bytes

    """
    e_padded = "FF" * esize if not e_data else e_data
    m_padded = "FF" * msize if not m_data else m_data
    b_padded = "FF" * bsize if not b_data else b_data

    # Format sizes as 32-byte hex strings
    bsize_hex = format(bsize, "032x")
    esize_hex = format(esize, "032x")
    msize_hex = format(msize, "032x")

    # Concatenate all parts
    input_hex = bsize_hex + esize_hex + msize_hex + e_padded + m_padded + b_padded
    return bytes.fromhex(input_hex)


def generate_invalid_inputs_cases():
    """Generate test cases for invalid ModExp inputs."""
    return [
        pytest.param(bytes(), bytes(), False, id="zero-length-calldata"),
        pytest.param(
            create_modexp_input(10, 11, 12, b_data="FF" * 9),
            bytes(),
            False,
            id="b-too-short",
        ),
        pytest.param(
            create_modexp_input(10, 11, 12, m_data="FF" * 10),
            bytes(),
            False,
            id="m-too-short",
        ),
        pytest.param(
            create_modexp_input(10, 11, 12, e_data="FF" * 11),
            bytes(),
            False,
            id="e-too-short",
        ),
        pytest.param(
            create_modexp_input(0, 0, 0),
            bytes(),
            False,
            id="all-zeros",
        ),
    ]


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,call_succeeds",
    generate_invalid_inputs_cases(),
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
