"""
abstract: Tests [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939)
    Test cases for [EIP-7939: Count leading zeros (CLZ) opcode](https://eips.ethereum.org/EIPS/eip-7939).
"""

import pytest

from ethereum_test_tools import Account, Alloc, StateTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7939.md"
REFERENCE_SPEC_VERSION = "c8321494fdfbfda52ad46c3515a7ca5dc86b857c"

CLZ_GAS_COST = 3


@pytest.mark.valid_from("Osaka")
@pytest.mark.parametrize("bits", range(257))
def test_clz(state_test: StateTestFiller, bits: int, pre: Alloc):
    """Test CLZ opcode."""
    value = 2**256 - 1 >> bits
    contract_address = pre.deploy_contract(
        Op.SSTORE(0, Op.CLZ(value))
        + Op.SSTORE(1, Op.SUB(Op.GAS + Op.SWAP1, Op.GAS + Op.POP(Op.CLZ(value)))),
        storage={"0x00": "0xdeadbeef", "0x01": "0xdeadbeef"},
    )
    sender = pre.fund_eoa()

    tx = Transaction(to=contract_address, sender=sender, gas_limit=200_000)

    post = {
        # gas cost calculation adds the cost of PUSH (3), POP (2) and GAS (2) to the costs of CLZ
        # TODO: read gas costs of these opcode from fork
        contract_address: Account(storage={"0x00": bits, "0x01": CLZ_GAS_COST + 3 + 2 + 2}),
    }

    state_test(pre=pre, post=post, tx=tx)
