"""
Test EIP-6780: remove selfdestruct
"""
from typing import Dict

from ethereum_test_forks import Cancun, is_fork
from ethereum_test_forks.forks.upcoming import Cancun

from ethereum_test_tools import (
    Account,
    CodeGasMeasure,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
    to_address,
    to_hash,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6780.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"

@test_from(fork=Cancun)
def test_eip6780_create_selfdestruct_same_tx(fork):
        env = Environment(
                coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
                difficulty=0x20000,
                gas_limit=10000000000,
                number=1,
                timestamp=1000,
        )
        post: Dict[Any, Any] = {}

        test_ops =[
                "6032",
                "601c",
                "6000",
                "39", # codecopy
                # create account
                "6032",
                "6000",
                "6000", # zero value
                "f0"
                # TODO call created account
                "6000",
                "6000",
                "6000",
                "6000",
                "6000",
                "85", # dup the returned address
                "45", # pass gas limit
                "f1",
                "00" # STOP
                # payload:
                # copy inner payload to memory
                "6008",
                "600c",
                "6000",
                "39", # codecopy
                # return payload
                "6008",
                "6000",
                "f3",
                # inner payload:
                "60016000556000ff"
        ] 
        test_ops = "".join(test_ops)

        post['0x5fef11c6545be552c986e9eaac3144ecf2258fd3'] = Account.NONEXISTENT

        pre = {
                TestAddress: Account(balance=1000000000000000000000),
        }
        tx = Transaction(
                ty=0x0,
                data=test_ops,
                chain_id=0x0,
                nonce=0,
                to=None,
                gas_limit=100000000,
                gas_price=10,
                protected=False,
        )

        yield StateTest(
                env=env,
                pre=pre,
                post=post,
                txs=[tx],
                tag="6780-create-inside-tx",
        )

@test_from(fork=Cancun)
def test_eip6780_selfdestruct_prev_created(fork):
        env = Environment(
                coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
                difficulty=0x20000,
                gas_limit=10000000000,
                number=1,
                timestamp=1000,
        )
        post: Dict[Any, Any] = {}

        post['0x1111111111111111111111111111111111111111'] = Account(
                        balance=0,
                        code="0x60016000556000ff"
        )
        post['0x0000000000000000000000000000000000000000'] = Account(
                        balance=1
        )

        pre = {
                TestAddress: Account(balance=1000000000000000000000),
                "0x1111111111111111111111111111111111111111": Account(
                        balance=1,
                        code="0x60016000556000ff"
                )
        }
        tx = Transaction(
                ty=0x0,
                data="",
                chain_id=0x0,
                nonce=0,
                to="0x1111111111111111111111111111111111111111",
                gas_limit=100000000,
                gas_price=10,
                protected=False,
        )

        yield StateTest(
                env=env,
                pre=pre,
                post=post,
                txs=[tx],
                tag="6780-create-inside-tx",
        )
