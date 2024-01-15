"""
Suicide scenario requested test
https://github.com/ethereum/execution-spec-tests/issues/381
"""

from typing import Dict, Union

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    Account,
    Environment,
    Initcode,
    StateTestFiller,
    TestAddress,
    Transaction,
    compute_create2_address,
    to_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-6780.md"
REFERENCE_SPEC_VERSION = "2f8299df31bb8173618901a03a8366a3183479b0"


@pytest.fixture
def env():  # noqa: D103
    return Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x020000,
        gas_limit=71794957647893862,
        number=1,
        timestamp=1000,
    )


@pytest.mark.valid_from("Merge")
@pytest.mark.parametrize(
    "create2_dest_already_in_state",
    (False, True),
)
def test_dynamic_create2_selfdestruct_collision(
    env: Environment,
    fork: Fork,
    create2_dest_already_in_state: bool,
    state_test: StateTestFiller,
):
    """Dynamic Create2->Suicide->Create2 collision scenario:"""
    """
    Perform a CREATE2, make sure that the initcode sets at least a couple of storage keys,
    then on a different call, in the same tx, perform a self-destruct.
    Then:
        a) on the same tx, attempt to recreate the contract   <=== Covered int this test
            1) and create2 contract already in the state
            2) and create2 contract is not in the state
        b) on a different tx, attempt to recreate the contract
    Perform a CREATE2, make sure that the initcode sets at least a couple of storage keys,
    then in a different tx, perform a self-destruct.
    Then:
        a) on the same tx, attempt to recreate the contract
        b) on a different tx, attempt to recreate the contract
    Verify that the test case described
    in https://wiki.hyperledger.org/pages/viewpage.action?pageId=117440824 is covered
    """

    first_create2_result = 1
    second_create2_result = 2

    address_to = to_address(0x0600)
    address_code = to_address(0x0601)
    address_create2_storage = to_address(0x0512)
    suicide_destination = to_address(0x03E8)

    create2_salt = 1
    initcode = Initcode(
        deploy_code=Op.SELFDESTRUCT(Op.PUSH20(suicide_destination)),
        initcode_prefix=Op.SSTORE(1, 1)
        + Op.CALL(Op.GAS(), Op.PUSH20(address_create2_storage), 0, 0, 0, 0, 0),
    )
    create2_address = compute_create2_address(address_code, create2_salt, initcode)

    pre = {
        address_to: Account(
            balance=100000000,
            nonce=0,
            code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.SSTORE(
                1, Op.CALL(Op.GAS(), Op.PUSH20(address_code), 0, 0, Op.CALLDATASIZE(), 0, 0)
            )
            + Op.SSTORE(2, 1),
            storage={0x01: 0xFF},
        ),
        address_code: Account(
            balance=1000000000000000000,
            nonce=0,
            code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.SSTORE(first_create2_result, Op.CREATE2(7, 0, Op.CALLDATASIZE(), create2_salt))
            + Op.CALL(Op.GAS(), Op.SLOAD(1), 3, 0, 0, 0, 0)
            + Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.SSTORE(second_create2_result, Op.CREATE2(5, 0, Op.CALLDATASIZE(), create2_salt)),
            storage={0x02: 0xFF},
        ),
        address_create2_storage: Account(
            balance=7000000000000000000,
            nonce=0,
            code=Op.SSTORE(1, 1),
            storage={},
        ),
        TestAddress: Account(
            balance=7000000000000000000,
            nonce=0,
            code="0x",
            storage={},
        ),
    }

    if create2_dest_already_in_state:
        pre[create2_address] = Account(balance=13, nonce=1, storage={})

    post: Dict[str, Union[Account, object]] = {}
    if create2_dest_already_in_state:
        # Check that create2 account is unchanged
        post[create2_address] = Account(balance=13, nonce=1, code="0x", storage={})
        # The create2 collision causes all the code to go out of gas
        post[address_to] = Account(storage={0x01: 0x00, 0x02: 0x01})
        post[suicide_destination] = Account.NONEXISTENT
        post[address_create2_storage] = Account(storage={0x01: 0x00})
        post[address_code] = Account(
            storage={first_create2_result: 0x00, second_create2_result: 0xFF}
        )
    else:
        # Make sure the address_code call has worked
        post[address_to] = Account(storage={0x01: 0x01, 0x02: 0x01})
        # Check what value has been transferred by suicide (7 on create and 3 with the call)
        post[suicide_destination] = Account(balance=10)
        # Make sure the CREATE2 address performed storage operations
        post[address_create2_storage] = Account(storage={0x01: 0x01})
        # Make sure the second CREATE2 attempt is failing
        post[address_code] = Account(
            storage={first_create2_result: create2_address, second_create2_result: 0x00}
        )
        # Make sure selfdestruct cleans the account
        post[create2_address] = Account.NONEXISTENT

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to=address_to,
        gas_price=10,
        protected=False,
        data=initcode.bytecode if initcode.bytecode is not None else bytes(),
        gas_limit=5000000,
        value=0,
    )

    state_test(env=env, pre=pre, post=post, tx=tx)
