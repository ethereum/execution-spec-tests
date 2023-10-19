"""
Test Account Self-destruction and Re-creation
"""

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    Account,
    Environment,
    Initcode,
    StateTestFiller,
    TestAddress,
    Transaction,
    Yul,
    compute_create_address,
    compute_create2_address,
)

@pytest.mark.valid_from("Constantinople")
@pytest.mark.valid_until("Shanghai")
def test_recreate(state_test: StateTestFiller, fork: Fork):
    env = Environment()

    creator_address = 0x100
    creator_contract_code=(
            Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
            + Op.CREATE2(0, 0, Op.CALLDATASIZE, 0)
        )

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000
        ),
        creator_address: Account(
            code=creator_contract_code,
            nonce=1,
        ),
    }

    deploy_code=Yul(
        """
        {
            switch callvalue()
            case 0 {
                selfdestruct(0)
            }
            default {
                sstore(0, callvalue())
            }
        }
        """
        ,
        fork=fork,
    )

    initcode = Initcode(deploy_code=deploy_code).bytecode

    tx_create = Transaction(
        ty=0,
        nonce=0,
        gas_limit=100000000,
        gas_price=10,
        to=creator_address,
        data=initcode,
    )

    created_contract_address = compute_create2_address(address=creator_address, salt=0, initcode=initcode)

    value = 1
    tx_set_storage = Transaction(
        ty=0,
        nonce=1,
        gas_limit=100000000,
        gas_price=10,
        to=created_contract_address,
        value=value,
    )

    post = {
        created_contract_address: Account(
            nonce=1,
            code=deploy_code,
            storage={0x00: value},
        ),
    }
    state_test(env=env, pre=pre, post=post, txs=[tx_create, tx_set_storage])
