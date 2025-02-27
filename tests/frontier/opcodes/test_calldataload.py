"""
abstract: Test `CALLDATALOAD`
    Test the `CALLDATALOAD` opcodes.

"""

import pytest

from ethereum_test_forks import Fork, Frontier, Homestead
from ethereum_test_tools import (
    Account,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op


@pytest.mark.parametrize(
    "calldataload_offset,memory_preset_code,call_args_size,expected_calldataload_memory",
    [
        pytest.param(
            0x00,
            Op.MSTORE8(offset=0x0, value=0x25) + Op.MSTORE8(offset=0x1, value=0x60),
            0x02,
            0x2560000000000000000000000000000000000000000000000000000000000000,
            id="calldata_short_start_0",
        ),
        pytest.param(
            0x01,
            Op.MSTORE(
                offset=0x0,
                value=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
            )
            + Op.MSTORE8(offset=0x20, value=0x23),
            0x21,
            0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF23,
            id="calldata_sufficient_with_offset",
        ),
        pytest.param(
            0x05,
            Op.MSTORE(
                offset=0x0,
                value=0x123456789ABCDEF0000000000000000000000000000000000000000000000000,
            )
            + Op.MSTORE8(offset=0x20, value=0x0)
            + Op.MSTORE8(offset=0x21, value=0x24),
            0x22,
            0xBCDEF00000000000000000000000000000000000000000000000000024000000,
            id="calldata_partial_word_at_offset",
        ),
    ],
)
@pytest.mark.valid_from("Frontier")
def test_calldataload(
    state_test: StateTestFiller,
    fork: Fork,
    calldataload_offset: int,
    memory_preset_code: Bytecode,
    call_args_size: int,
    expected_calldataload_memory: int,
    pre: Alloc,
):
    """
     Test `CALLDATACOPY` opcode.

    This test verifies that `CALLDATALOAD` correctly retrieves a 32-byte word
    from calldata at different offsets, handling various edge cases.

    Test Cases:

    calldata_short_start_0:
       - The calldata size is less than 32 bytes.
       - `CALLDATALOAD` starts at offset 0x00.
       - The result should correctly pad missing bytes with zeros.

    calldata_sufficient_with_offset:
       - The calldata size is greater than 32 bytes.
       - `CALLDATALOAD` starts at a valid offset within calldata**.
       - A full 32-byte word is retrieved successfully.

    calldata_partial_word_at_offset:
       - The calldata size is greater than 32 bytes but `CALLDATALOAD` starts at an offset
         where `offset + 32` exceeds the calldata size.
       - The result should return the available bytes, and the rest should be zero-padded.

     Based on https://github.com/ethereum/tests/blob/develop/src/GeneralStateTestsFiller/VMTests/vmTests/calldataloadFiller.yml
    """
    env = Environment()
    sender = pre.fund_eoa()
    post = {}

    # Deploy the contract that will store the calldate
    sstore_contract = pre.deploy_contract(
        code=(Op.SSTORE(key=0x0, value=Op.CALLDATALOAD(offset=calldataload_offset)))
    )

    # Deploy the contract that will forward the calldata to the first contract
    calldata_contract = pre.deploy_contract(
        code=(
            memory_preset_code
            + Op.CALL(
                gas=Op.SUB(Op.GAS, 20000),
                address=sstore_contract,
                args_size=call_args_size,
            )
        )
    )

    validation_contract = pre.deploy_contract(
        code=(
            Op.CALL(
                gas=Op.SUB(Op.GAS, 20000),
                address=calldata_contract,
            )
        )
    )

    tx = Transaction(
        gas_limit=100000,
        protected=False if fork in [Frontier, Homestead] else True,
        to=validation_contract,
        sender=sender,
    )

    post[sstore_contract] = Account(storage={0x0: expected_calldataload_memory})

    state_test(env=env, pre=pre, post=post, tx=tx)
