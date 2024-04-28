"""
Test good and bad EOFCREATE cases
"""

import pytest

from ethereum_test_tools import (
    Account,
    Environment,
    StateTestFiller,
    TestAddress,
    compute_eofcreate_address,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.eof.v1.constants import NON_RETURNING_SECTION
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import (
    default_address,
    fixed_address,
    simple_transaction,
    smallest_initcode_subcontainer,
    smallest_runtime_subcontainer,
)
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


def test_simple_eofcreate(
    state_test: StateTestFiller,
):
    """
    Verifies a simple EOFCREATE case
    """
    env = Environment()
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0)) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=smallest_initcode_subcontainer),
                ],
                data=b"abcdef",
            )
        ),
    }
    # Storage in 0 should have the address,
    post = {
        default_address: Account(
            storage={
                0: compute_eofcreate_address(default_address, 0, smallest_initcode_subcontainer)
            }
        )
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_eofcreate_then_call(
    state_test: StateTestFiller,
):
    """
    Verifies a simple EOFCREATE case, and then calls the deployed contract
    """
    env = Environment()
    callable_contract = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, 1) + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
        ]
    )
    callable_contract_initcode = Container(
        sections=[
            Section.Code(
                code=Op.RETURNCONTRACT[0](0, 0),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Container(container=callable_contract),
        ]
    )

    callable_address = compute_eofcreate_address(default_address, 0, callable_contract_initcode)
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0))
                        + Op.EXTCALL(callable_address, 0, 0, 0)
                        + Op.SSTORE(1, 1)
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=callable_contract_initcode),
                ],
            )
        ),
    }
    # Storage in 0 should have the address,
    #
    post = {
        default_address: Account(storage={0: callable_address, 1: 1}),
        callable_address: Account(storage={0: 1}),
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


@pytest.mark.parametrize(
    "auxdata_bytes",
    [
        b"aabbccddeeff",
        b"aabbccddeeffgghhii",
        b"aabbcc",
    ],
    ids=["exact", "extra", "short"],
)
def test_auxdata_variations(state_test: StateTestFiller, auxdata_bytes: bytes):
    """
    Verifies that auxdata bytes are correctly handled in RETURNCONTRACT
    """
    env = Environment()
    auxdata: int = int.from_bytes(auxdata_bytes, byteorder="big")
    auxdata_size = len(auxdata_bytes)

    runtime_subcontainer = Container(
        name="Runtime Subcontainer with truncated data",
        sections=[
            Section.Code(
                code=Op.STOP, code_inputs=0, code_outputs=NON_RETURNING_SECTION, max_stack_height=0
            ),
            Section.Data(data=b"AABBCC", custom_size=18),
        ],
    )

    initcode_subcontainer = Container(
        name="Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.MSTORE(0, auxdata) + Op.RETURNCONTRACT[0](0, auxdata_size),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Container(container=runtime_subcontainer),
        ],
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0)) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=initcode_subcontainer),
                ]
            )
        ),
    }

    # Storage in 0 should have the address,
    post = {
        default_address: Account(
            storage={
                0: compute_eofcreate_address(default_address, 0, initcode_subcontainer)
                if auxdata_size >= 12
                else b"\0"
            }
        )
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_calldata(state_test: StateTestFiller):
    """
    Verifies CALLDATA passing through EOFCREATE
    """
    env = Environment()

    initcode_subcontainer = Container(
        name="Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
                + Op.SSTORE(0, Op.MLOAD(0))
                + Op.RETURNCONTRACT[0](0, Op.CALLDATASIZE),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=3,
            ),
            Section.Container(container=smallest_runtime_subcontainer),
        ],
    )

    calldata_bytes = b"\x45" * 32
    calldata_size = len(calldata_bytes)
    calldata = int.from_bytes(calldata_bytes, "big")
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.MSTORE(0, calldata)
                        + Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, calldata_size))
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=initcode_subcontainer),
                ]
            )
        ),
    }

    # deployed contract is smallest plus data
    deployed_contract = Container(
        name="deployed contract",
        sections=[
            *smallest_runtime_subcontainer.sections,
            Section.Data(data=calldata_bytes),
        ],
    )
    # factory contract Storage in 0 should have the created address,
    # created contract storage in 0 should have the calldata
    created_address = compute_eofcreate_address(default_address, 0, initcode_subcontainer)
    post = {
        default_address: Account(storage={0: created_address}),
        created_address: Account(code=deployed_contract, storage={0: calldata}),
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_eofcreate_in_initcode(
    state_test: StateTestFiller,
):
    """
    Verifies an EOFCREATE occuring within initcode creaes that contract
    """
    nested_initcode_subcontainer = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0))
                + Op.SSTORE(1, 1)
                + Op.RETURNCONTRACT[1](0, 0),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=4,
            ),
            Section.Container(container=smallest_initcode_subcontainer),
            Section.Container(container=smallest_runtime_subcontainer),
        ]
    )

    env = Environment()
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0)) + Op.SSTORE(1, 1) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=nested_initcode_subcontainer),
                ]
            )
        ),
    }

    outer_address = compute_eofcreate_address(default_address, 0, nested_initcode_subcontainer)
    inner_address = compute_eofcreate_address(outer_address, 0, smallest_initcode_subcontainer)
    post = {
        default_address: Account(storage={0: outer_address, 1: 1}),
        outer_address: Account(storage={0: inner_address, 1: 1}),
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_eofcreate_in_initcode_reverts(
    state_test: StateTestFiller,
):
    """
    Verifies an EOFCREATE occuring in an initcode is rolled back when the initcode reverts
    """
    nested_initcode_subcontainer = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0)) + Op.SSTORE(1, 1) + Op.REVERT(0, 0),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=4,
            ),
            Section.Container(container=smallest_initcode_subcontainer),
            Section.Container(container=smallest_runtime_subcontainer),
        ]
    )

    env = Environment()
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0)) + Op.SSTORE(1, 1) + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=nested_initcode_subcontainer),
                ]
            )
        ),
    }

    outer_address = compute_eofcreate_address(default_address, 0, nested_initcode_subcontainer)
    inner_address = compute_eofcreate_address(outer_address, 0, smallest_initcode_subcontainer)
    post = {
        default_address: Account(storage={1: 1}),
        outer_address: Account.NONEXISTENT,
        inner_address: Account.NONEXISTENT,
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_return_data_cleared(
    state_test: StateTestFiller,
):
    """
    Verifies a teh return data is not re-used from a extcall but is cleared upon eofcreate
    """
    env = Environment()
    callable_address = fixed_address(1)
    callable_contract = Container(
        sections=[
            Section.Code(
                code=Op.MSTORE(0, 0x38363735333039) + Op.RETURN(0, 7),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            )
        ]
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EXTCALL(callable_address, 0, 0, 0))
                        + Op.SSTORE(1, Op.RETURNDATASIZE)
                        + Op.SSTORE(2, Op.EOFCREATE[0](0, 0, 0, 0))
                        + Op.SSTORE(3, Op.RETURNDATASIZE)
                        + Op.SSTORE(4, 1)
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=smallest_initcode_subcontainer),
                ],
            )
        ),
        callable_address: Account(code=callable_contract, nonce=1),
    }

    # Storage in 0 should have the address,
    new_contract_address = compute_eofcreate_address(
        default_address, 0, smallest_initcode_subcontainer
    )
    post = {
        default_address: Account(
            # slot 0 - EXTCALL result 0 / empty
            # slot 1 - returndatasize from extcall
            # slot 2 - eofcreate address
            # slot 3 - returndatasize from eofcreate
            # slot 4 - canary 1 for halts
            storage={
                0: 0,
                1: 7,
                2: new_contract_address,
                3: 0,
                4: 1,
            },
            nonce=1,
        ),
        callable_address: Account(nonce=1),
        new_contract_address: Account(nonce=1),
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_address_collision(
    state_test: StateTestFiller,
):
    """
    Verifies a simple EOFCREATE case
    """
    env = Environment()

    salt_zero_address = compute_eofcreate_address(
        default_address, 0, smallest_initcode_subcontainer
    )
    salt_one_address = compute_eofcreate_address(
        default_address, 1, smallest_initcode_subcontainer
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0))
                        + Op.SSTORE(1, Op.EOFCREATE[0](0, 0, 0, 0))
                        + Op.SSTORE(2, Op.EOFCREATE[0](0, 1, 0, 0))
                        + Op.SSTORE(3, 1)
                        + Op.STOP,
                        code_inputs=0,
                        code_outputs=NON_RETURNING_SECTION,
                        max_stack_height=4,
                    ),
                    Section.Container(container=smallest_initcode_subcontainer),
                ],
            )
        ),
        salt_one_address: Account(balance=1, nonce=1),
    }
    # Storage in 0 should have the address as no collision
    # Storage in 1 has an in-transaction collisions, so zero
    # Storage in 2 has a pre-existing collision, so zero
    # Storage 3 is a canary to detect Halts, should be 1
    post = {default_address: Account(storage={0: salt_zero_address, 3: 1})}

    # Multiple create fails is expensive, use an absurd amount of gas
    state_test(env=env, pre=pre, post=post, tx=simple_transaction(gas_limit=300_000_000_000))
