"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

from typing import Dict, Union

import pytest

from ethereum_test_forks import Shanghai
from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
)
from ethereum_test_tools.code import Yul
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "N/A"
REFERENCE_SPEC_VERSION = "N/A"


@pytest.mark.valid_from("Cancun")
def test_yul_coverage(
    state_test: StateTestFiller,
):
    """
    Use this test to fill the coverage which is not completed by using Op
    when converting from .json tests filled with yul and different solc evm versions
    """
    address_to = Address("A00000000000000000000000000000000000000A")
    missed_coverage = Address("B00000000000000000000000000000000000000B")
    uncalled_account = Address("C00000000000000000000000000000000000000C")

    pre = {
        address_to: Account(
            balance=1000000000000000000,
            nonce=0,
            code=Yul(
                """
            {
                let ok := call(gas(), 0xB00000000000000000000000000000000000000B, 0, 0, 0, 0, 0)
                mstore(0, ok)
                return(0, 32)
            }
            """,
                fork=Shanghai,
            ),
        ),
        missed_coverage: Account(
            balance=0,
            nonce=0,
            code=Op.SHL(0x0000000000000000000000000000000000000000000000000000000000000001, 0x00)
            + Op.SHR(0x0000000000000000000000000000000000000000000000000000000000000001, 0x00)
            + Op.SWAP1(0x0A, 0x0B)
            + Op.DUP2(0x01, 0x02)
            + Op.PUSH0()
            + Op.PUSH3(0x01, 0x01, 0x01)
            + Op.PUSH4(0x01, 0x02, 0x03, 0x04)
            + Op.POP(0x01),
            storage={},
        ),
        uncalled_account: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
        TestAddress: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
    }

    post: Dict[Address, Union[Account, object]] = {}

    tx = Transaction(
        nonce=0,
        gas_limit=100000,
        to=address_to,
        data=b"",
        value=0,
        access_list=[],
        max_fee_per_gas=10,
        max_priority_fee_per_gas=5,
    )

    state_test(env=Environment(), pre=pre, post=post, tx=tx)
