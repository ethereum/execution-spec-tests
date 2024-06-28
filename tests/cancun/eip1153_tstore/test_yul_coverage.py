"""
Ethereum Transient Storage EIP Tests
https://eips.ethereum.org/EIPS/eip-1153
"""

import pytest

from ethereum_test_forks import Shanghai
from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Environment,
    StateTestFiller,
    Transaction,
    Yul,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "N/A"
REFERENCE_SPEC_VERSION = "N/A"


@pytest.mark.valid_from("Cancun")
def test_yul_coverage(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    This test complete the coverage gaps by calling the codes, produced by yul compiler
    """
    pre.deploy_contract(
        address=Address("0xB00000000000000000000000000000000000000B"),
        balance=0,
        code=Op.SHL(0x0000000000000000000000000000000000000000000000000000000000000001, 0x00)
        + Op.SHR(0x0000000000000000000000000000000000000000000000000000000000000001, 0x00)
        + Op.PUSH1(0x0A)
        + Op.PUSH1(0x0B)
        + Op.PUSH1(0x0C)
        + Op.PUSH1(0x0D)
        + Op.PUSH1(0x0E)
        + Op.SWAP1()
        + Op.DUP1()
        + Op.DUP2()
        + Op.PUSH0()
        + Op.PUSH2(0x0102)
        + Op.PUSH3(0x010203)
        + Op.PUSH4(0x01020304)
        + Op.POP(0x01),
        storage={},
    )
    address_to = pre.deploy_contract(
        balance=1_000_000_000_000_000_000,
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
    )

    tx = Transaction(
        sender=pre.fund_eoa(7_000_000_000_000_000_000),
        gas_limit=100000,
        to=address_to,
        data=b"",
        value=0,
        access_list=[],
        max_fee_per_gas=10,
        max_priority_fee_per_gas=5,
    )

    state_test(env=Environment(), pre=pre, post={}, tx=tx)
