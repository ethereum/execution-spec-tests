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
from ethereum_test_tools.eof.v1.constants import (
    MAX_BYTECODE_SIZE,
    MAX_INITCODE_SIZE,
    NON_RETURNING_SECTION,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import (
    default_address,
    simple_transaction,
    smallest_initcode_subcontainer,
    smallest_runtime_subcontainer,
)
from .spec import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7620.md"
REFERENCE_SPEC_VERSION = "52ddbcdddcf72dd72427c319f2beddeb468e1737"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)


@pytest.mark.parametrize(
    "revert",
    [
        "",
        "08c379a0",
    ],
    ids=["empty", "Error(string)"],
)
def test_initcode_revert(state_test: StateTestFiller, revert: str):
    """
    Verifies proper handling of REVERT in initcode
    """
    env = Environment()
    revert_bytes = bytes.fromhex(revert)
    revert_size = len(revert_bytes)

    initcode_subcontainer = Container(
        name="Initcode Subcontainer that reverts",
        sections=[
            Section.Code(
                code=Op.MSTORE(0, int.from_bytes(revert_bytes, "big"))
                + Op.REVERT(32 - revert_size, revert_size),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
        ],
    )

    factory_contract = Container(
        name="factory contract",
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, 0))
                + Op.SSTORE(1, Op.RETURNDATASIZE)
                + Op.RETURNDATACOPY(Op.SUB(32, Op.RETURNDATASIZE), 0, Op.RETURNDATASIZE)
                + Op.SSTORE(2, Op.MLOAD(0))
                + Op.SSTORE(3, 3)  # just a canary
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=4,
            ),
            Section.Container(container=initcode_subcontainer),
        ],
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(code=factory_contract),
    }

    # Storage in 0 should have the address,
    post = {
        default_address: Account(
            storage={1: revert_size, 2: revert_bytes, 3: 3} if revert_size > 0 else {3: 3}
        )
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_initcode_aborts(
    state_test: StateTestFiller,
):
    """
    Verifies correct handling of a halt in EOF initcode
    """
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
                    Section.Container(
                        container=Container(
                            sections=[
                                Section.Code(
                                    code=Op.INVALID,
                                    code_inputs=0,
                                    code_outputs=NON_RETURNING_SECTION,
                                    max_stack_height=0,
                                )
                            ]
                        )
                    ),
                ]
            )
        ),
    }
    # Storage in 0 should have the address,
    post = {default_address: Account(storage={1: 1})}

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


"""
Size of the factory portion of test_eofcreate_deploy_sizes, but as the runtime code is dynamic, we
have to use a pre-calculated size
"""
factory_size = 30


@pytest.mark.parametrize(
    "target_deploy_size",
    [0x4000, 0x6000, 0x6001, 0xC000 - 30, 0xC001 - factory_size, 0xFFFF - factory_size],
    ids=["large", "max", "overmax", "initcodemax", "initcodeovermax", "64k-1"],
)
def test_eofcreate_deploy_sizes(
    state_test: StateTestFiller,
    target_deploy_size: int,
):
    """
    Verifies a mix of runtime contract sizes mixing success and multiple size failure modes.
    """
    env = Environment()

    runtime_container = Container(
        sections=[
            Section.Code(
                code=Op.JUMPDEST * (target_deploy_size - len(smallest_runtime_subcontainer))
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=0,
            ),
        ]
    )

    initcode_subcontainer = Container(
        name="Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.RETURNCONTRACT[0](0, 0),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Container(container=runtime_container),
        ],
    )

    assert factory_size == (
        len(initcode_subcontainer) - len(runtime_container)
    ), "factory_size is wrong, expected factory_size is %d, calculated is %d" % (
        factory_size,
        len(initcode_subcontainer),
    )

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
                    Section.Container(container=initcode_subcontainer),
                ]
            )
        ),
    }
    # Storage in 0 should have the address,
    # Storage 1 is a canary of 1 to make sure it tried to execute, which also covers cases of
    #   data+code being greater than initcode_size_max, which is allowed.
    post = {
        default_address: Account(
            storage={
                0: compute_eofcreate_address(default_address, 0, initcode_subcontainer)
                if target_deploy_size <= MAX_BYTECODE_SIZE
                else 0,
                1: 1,
            }
        )
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


@pytest.mark.parametrize(
    "auxdata_bytes",
    [
        b"a" * (MAX_BYTECODE_SIZE - len(smallest_runtime_subcontainer)),
        b"a" * (MAX_BYTECODE_SIZE - len(smallest_runtime_subcontainer) + 1),
        b"a" * (0x10000 - 60),
        b"a" * (0x10000 - 1),
        b"a" * (0x10000),
        b"a" * (0x10001),
    ],
    ids=["maxcode", "overmaxcode", "almost64k", "64k-1", "64k+1", "over64k"],
)
def test_auxdata_size_failures(state_test: StateTestFiller, auxdata_bytes: bytes):
    """
    Exercises a number of auxdata size violations, and one maxcode success
    """
    env = Environment()
    auxdata_size = len(auxdata_bytes)

    initcode_subcontainer = Container(
        name="Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
                + Op.RETURNCONTRACT[0](0, Op.CALLDATASIZE),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=3,
            ),
            Section.Container(container=smallest_runtime_subcontainer),
        ],
    )

    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(
            code=Container(
                sections=[
                    Section.Code(
                        code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
                        + Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, Op.CALLDATASIZE))
                        + Op.SSTORE(1, 1)
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

    deployed_container_size = len(smallest_runtime_subcontainer) + auxdata_size

    # Storage in 0 will have address in first test, 0 in all other cases indicating failure
    # Storage 1 in 1 is a canary to see if EOFCREATE opcode halted
    post = {
        default_address: Account(
            storage={
                0: compute_eofcreate_address(default_address, 0, initcode_subcontainer)
                if deployed_container_size <= MAX_BYTECODE_SIZE
                else 0,
                1: 1,
            }
        )
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction(payload=auxdata_bytes))


def test_eofcreate_insufficient_stipend(
    state_test: StateTestFiller,
):
    """
    Exercises an EOFCREATE that fails because the calling account does not have enough ether to
    pay the stipend
    """
    env = Environment()
    initcode_container = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](10**12, 0, 0, 0)) + Op.SSTORE(1, 1) + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=4,
            ),
            Section.Container(container=smallest_initcode_subcontainer),
        ]
    )
    pre = {
        TestAddress: Account(balance=10**11, nonce=1),
        default_address: Account(code=initcode_container),
    }
    # create will fail but not trigger a halt, so canary at storage 1 should be set
    # also validate target created contract fails
    post = {
        default_address: Account(storage={1: 1}),
        compute_eofcreate_address(default_address, 0, initcode_container): Account.NONEXISTENT,
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction())


def test_insufficient_initcode_gas(
    state_test: StateTestFiller,
):
    """
    Excercises an EOFCREATE when there is not enough gas for the initcode charge
    """
    env = Environment()

    initcode_data = b"a" * 0x5000
    initcode_container = Container(
        name="Large Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.RETURNCONTRACT[0](0, 0),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Container(container=smallest_runtime_subcontainer),
            Section.Data(data=initcode_data),
        ],
    )

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
                    Section.Container(container=initcode_container),
                ],
            )
        ),
    }
    # enough gas for everything but EVM opcodes and EIP-150 reserves
    gas_limit = 21_000 + 32_000 + (len(initcode_data) + 31) // 32 * 6
    # out_of_gas is triggered, so canary won't set value
    # also validate target created contract fails
    post = {
        default_address: Account(storage={}),
        compute_eofcreate_address(default_address, 0, initcode_container): Account.NONEXISTENT,
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction(gas_limit=gas_limit))


def test_insufficient_gas_memory_expansion(
    state_test: StateTestFiller,
):
    """
    Excercises an EOFCREATE when the memory for auxdata has not been expanded but is requested
    """
    env = Environment()

    auxdata_size = 0x5000
    initcode_container = Container(
        sections=[
            Section.Code(
                code=Op.SSTORE(0, Op.EOFCREATE[0](0, 0, 0, auxdata_size))
                + Op.SSTORE(1, 1)
                + Op.STOP,
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=4,
            ),
            Section.Container(container=smallest_initcode_subcontainer),
        ],
    )
    pre = {
        TestAddress: Account(balance=10**21, nonce=1),
        default_address: Account(code=initcode_container),
    }
    # enough gas for everything but EVM opcodes and EIP-150 reserves
    initcode_container_words = (len(initcode_container) + 31) // 32
    auxdata_size_words = (auxdata_size + 31) // 32
    gas_limit = (
        21_000
        + 32_000
        + initcode_container_words * 6
        + 3 * auxdata_size_words
        + auxdata_size_words * auxdata_size_words // 512
    )
    # out_of_gas is triggered, so canary won't set value
    # also validate target created contract fails
    post = {
        default_address: Account(storage={}),
        compute_eofcreate_address(default_address, 0, initcode_container): Account.NONEXISTENT,
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction(gas_limit=gas_limit))


def test_insufficient_returncontract_auxdata_gas(
    state_test: StateTestFiller,
):
    """
    Excercises an EOFCREATE when there is not enough gas for the initcode charge
    """
    env = Environment()

    auxdata_size = 0x5000
    initcode_container = Container(
        name="Large Initcode Subcontainer",
        sections=[
            Section.Code(
                code=Op.RETURNCONTRACT[0](0, auxdata_size),
                code_inputs=0,
                code_outputs=NON_RETURNING_SECTION,
                max_stack_height=2,
            ),
            Section.Container(container=smallest_runtime_subcontainer),
        ],
    )

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
                    Section.Container(container=initcode_container),
                ],
            )
        ),
    }
    # enough gas for everything but EVM opcodes and EIP-150 reserves
    initcode_container_words = (len(initcode_container) + 31) // 32
    auxdata_size_words = (auxdata_size + 31) // 32
    gas_limit = (
        21_000
        + 32_000
        + initcode_container_words * 6
        + 3 * auxdata_size_words
        + auxdata_size_words * auxdata_size_words // 512
    )
    # out_of_gas is triggered, so canary won't set value
    # also validate target created contract fails
    post = {
        default_address: Account(storage={}),
        compute_eofcreate_address(default_address, 0, initcode_container): Account.NONEXISTENT,
    }

    state_test(env=env, pre=pre, post=post, tx=simple_transaction(gas_limit=gas_limit))
