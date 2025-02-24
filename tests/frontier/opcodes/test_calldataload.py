"""
abstract: Test `CALLDATALOAD`
    Test the `CALLDATALOAD` opcodes.

"""

import pytest

from ethereum_test_forks import Frontier, Homestead
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
    "sstore_test_opcode,calldata_opcode,validate_length,expected_storage",
    [
        (
            Bytecode(Op.SSTORE(key=0x0, value=Op.CALLDATALOAD(offset=0x0))),
            Bytecode(Op.MSTORE8(offset=0x0, value=0x25) + Op.MSTORE8(offset=0x1, value=0x60)),
            0x02,
            (
                Account(
                    storage={
                        0x00: 0x2560000000000000000000000000000000000000000000000000000000000000
                    }
                )
            ),
        ),
        (
            Bytecode(Op.SSTORE(key=0x0, value=Op.CALLDATALOAD(offset=0x01))),
            Bytecode(
                Op.MSTORE(
                    offset=0x0,
                    value=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
                )
                + Op.MSTORE8(offset=0x20, value=0x23),
            ),
            0x21,
            (
                Account(
                    storage={
                        0x00: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF23
                    }
                )
            ),
        ),
        (
            Bytecode(Op.SSTORE(key=0x0, value=Op.CALLDATALOAD(offset=0x05))),
            Bytecode(
                Op.MSTORE(
                    offset=0x0,
                    value=0x123456789ABCDEF0000000000000000000000000000000000000000000000000,
                )
                + Op.MSTORE8(offset=0x20, value=0x0)
                + Op.MSTORE8(offset=0x21, value=0x24),
            ),
            0x22,
            (
                Account(
                    storage={
                        0x00: 0xBCDEF00000000000000000000000000000000000000000000000000024000000
                    }
                )
            ),
        ),
    ],
    ids=["two_bytes", "word_n_byte", "34_bytes"],
)
@pytest.mark.valid_from("Frontier")
def test_calldataload(
    state_test: StateTestFiller,
    fork: str,
    sstore_test_opcode: Bytecode,
    calldata_opcode: Bytecode,
    validate_length: int,
    expected_storage: Account,
    pre: Alloc,
):
    """
    Test `CALLDATACOPY` opcode.

    Based on https://github.com/ethereum/tests/blob/develop/src/GeneralStateTestsFiller/VMTests/vmTests/calldataloadFiller.yml
    """
    env = Environment()
    sender = pre.fund_eoa()
    post = {}

    # Deploy the contract that will store the calldate
    sstore_contract = pre.deploy_contract(sstore_test_opcode)

    # Deploy the contract that will forward the calldata to the first contract
    calldata_contract = pre.deploy_contract(
        code=(
            calldata_opcode
            + Op.CALL(
                gas=0xFFFFFF,
                address=sstore_contract,
                value=0x0,
                args_offset=0x0,
                args_size=validate_length,
                ret_offset=0x0,
                ret_size=0x0,
            )
        )
    )

    validation_contract = pre.deploy_contract(
        code=(
            Op.CALL(
                gas=0xFFFFFF,
                address=calldata_contract,
                value=0x0,
                args_offset=0x0,
                args_size=0x0,
                ret_offset=0x0,
                ret_size=0x0,
            )
        )
    )

    tx = Transaction(
        data=b"\x01",
        gas_limit=100_000,
        gas_price=0x0A,
        protected=False if fork in [Frontier, Homestead] else True,
        to=validation_contract,
        value=0x01,
        sender=sender,
    )

    post[sstore_contract] = expected_storage

    state_test(env=env, pre=pre, post=post, tx=tx)
