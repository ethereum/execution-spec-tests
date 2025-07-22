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


@pytest.mark.parametrize(
    "modexp_input,modexp_expected,call_succeeds",
    [
        pytest.param(bytes(), bytes(), False, id="zero-length-calldata"),
        pytest.param(
            bytes.fromhex(
                format(10, "032x")  # Bsize
                + format(11, "032x")  # Esize
                + format(12, "032x")  # Msize
                + "FF" * 9  # E
                + "FF" * 11  # M
                + "FF" * 12  # B
            ),
            bytes(),
            False,
            id="b-too-short",
        ),
        pytest.param(
            bytes.fromhex(
                format(10, "032x")  # Bsize
                + format(11, "032x")  # Esize
                + format(12, "032x")  # Msize
                + "FF" * 10  # E
                + "FF" * 10  # M
                + "FF" * 12  # B
            ),
            bytes(),
            False,
            id="m-too-short",
        ),
        pytest.param(
            bytes.fromhex(
                format(10, "032x")  # Bsize
                + format(11, "032x")  # Esize
                + format(12, "032x")  # Msize
                + "FF" * 10  # E
                + "FF" * 11  # M
                + "FF" * 11  # B
            ),
            bytes(),
            False,
            id="e-too-short",
        ),
        # Not sure if this is valid
        pytest.param(
            bytes.fromhex(
                format(0, "032x")  # Bsize
                + format(0, "032x")  # Esize
                + format(0, "032x")  # Msize
            ),
            bytes(),
            False,
            id="all-zeros",
        ),
    ],
)
@EIPChecklist.Precompile.Test.Inputs.AllZeros
def test_modexp_invalid(
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
    """Test ModExp gas cost using the test vectors from EIP-7883."""
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
    """Test ModExp entry points."""
    tx = Transaction(
        to=Spec.MODEXP_ADDRESS,
        sender=pre.fund_eoa(),
        data=bytes(modexp_input),
        gas_limit=tx_gas_limit,
    )
    state_test(pre=pre, tx=tx, post={})
