"""
Suicide scenario requested test
https://github.com/ethereum/execution-spec-tests/issues/381
"""

from typing import Dict, Union

import pytest

from ethereum_test_forks import Cancun, Fork
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
    (True, False),
)
@pytest.mark.parametrize(
    "call_create2_contract_in_between",
    (True, False),
)
@pytest.mark.parametrize(
    "call_create2_contract_at_the_end",
    (True, False),
)
def test_dynamic_create2_selfdestruct_collision(
    env: Environment,
    fork: Fork,
    create2_dest_already_in_state: bool,
    call_create2_contract_in_between: bool,
    call_create2_contract_at_the_end: bool,
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

    # Storage locations
    create2_constructor_worked = 1
    first_create2_result = 2
    second_create2_result = 3
    code_worked = 4

    # Pre-Existing Addresses
    address_zero = to_address(0x00)
    address_to = to_address(0x0600)
    address_code = to_address(0x0601)
    address_create2_storage = to_address(0x0512)
    suicide_destination = to_address(0x03E8)
    suicide_destination_original = to_address(0x03E9)

    # CREATE2 Initcode
    create2_salt = 1
    deploy_code = Op.SELFDESTRUCT(Op.PUSH20(suicide_destination))
    initcode = Initcode(
        deploy_code=deploy_code,
        initcode_prefix=Op.SSTORE(create2_constructor_worked, 1)
        + Op.CALL(Op.GAS(), Op.PUSH20(address_create2_storage), 0, 0, 0, 0, 0),
    )

    # Created addresses
    create2_address = compute_create2_address(address_code, create2_salt, initcode)
    call_address_in_between = create2_address if call_create2_contract_in_between else address_zero
    call_address_in_the_end = create2_address if call_create2_contract_at_the_end else address_zero

    # Values
    first_create2_value = 3
    first_call_value = 5
    second_create2_value = 7
    second_call_value = 11
    pre_existing_create2_balance = 13

    pre = {
        address_to: Account(
            balance=100000000,
            nonce=0,
            code=Op.JUMPDEST()
            # Make a subcall that do CREATE2 and returns its the result
            + Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.CALL(
                100000, Op.PUSH20(address_code), first_create2_value, 0, Op.CALLDATASIZE(), 0, 32
            )
            + Op.SSTORE(
                first_create2_result,
                Op.MLOAD(0),
            )
            # Call to the created account to trigger selfdestruct
            + Op.CALL(100000, Op.PUSH20(call_address_in_between), first_call_value, 0, 0, 0, 0)
            # Make a subcall that do CREATE2 collision and returns its the result
            + Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.CALL(
                100000, Op.PUSH20(address_code), second_create2_value, 0, Op.CALLDATASIZE(), 0, 32
            )
            + Op.SSTORE(
                second_create2_result,
                Op.MLOAD(0),
            )
            # Call to the created account to trigger selfdestruct
            + Op.CALL(100000, Op.PUSH20(call_address_in_the_end), second_call_value, 0, 0, 0, 0)
            + Op.SSTORE(code_worked, 1),
            storage={first_create2_result: 0xFF, second_create2_result: 0xFF},
        ),
        address_code: Account(
            balance=0,
            nonce=0,
            code=Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
            + Op.MSTORE(
                0,
                Op.CREATE2(Op.SELFBALANCE(), 0, Op.CALLDATASIZE(), create2_salt),
            )
            + Op.RETURN(0, 32),
            storage={},
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
        pre[create2_address] = Account(
            balance=pre_existing_create2_balance,
            nonce=1,
            code=Op.SELFDESTRUCT(Op.PUSH20(suicide_destination_original)),
            storage={},
        )

    post: Dict[str, Union[Account, object]] = {}
    if create2_dest_already_in_state:
        # The create2 collision causes all the code to go out of gas and return 0x00
        post[address_to] = Account(
            storage={code_worked: 0x01, first_create2_result: 0x00, second_create2_result: 0x00}
        )
        post[address_create2_storage] = Account(storage={create2_constructor_worked: 0x00})

        if call_create2_contract_in_between:
            if fork >= Cancun:
                post[create2_address] = Account(balance=0, nonce=1, code=pre[create2_address].code)
            else:
                post[create2_address] = Account.NONEXISTENT
            post[suicide_destination] = Account.NONEXISTENT

            if call_create2_contract_at_the_end:
                post[suicide_destination_original] = Account(
                    balance=(pre_existing_create2_balance + first_call_value + second_call_value)
                )
            else:
                post[suicide_destination_original] = Account(
                    balance=(pre_existing_create2_balance + first_call_value)
                )
        else:
            if call_create2_contract_at_the_end:
                if fork >= Cancun:
                    post[create2_address] = Account(
                        balance=0, nonce=1, code=pre[create2_address].code
                    )
                else:
                    post[create2_address] = Account.NONEXISTENT
                post[suicide_destination_original] = Account(
                    balance=pre_existing_create2_balance + second_call_value
                )
            else:
                post[create2_address] = Account(
                    balance=pre_existing_create2_balance,
                    nonce=1,
                    code=pre[create2_address].code,
                    storage={},
                )
                post[suicide_destination_original] = Account.NONEXISTENT

    else:
        post[address_to] = Account(
            storage={
                code_worked: 0x01,
                first_create2_result: create2_address,
                second_create2_result: 0x00,
            }
        )
        post[address_create2_storage] = Account(storage={create2_constructor_worked: 0x01})

        if call_create2_contract_in_between:
            if call_create2_contract_at_the_end:
                post[suicide_destination] = Account(
                    balance=first_create2_value + first_call_value + second_call_value
                )
            else:
                post[suicide_destination] = Account(balance=first_create2_value + first_call_value)
            post[create2_address] = Account.NONEXISTENT
        else:
            if call_create2_contract_at_the_end:
                post[create2_address] = Account.NONEXISTENT
                post[suicide_destination] = Account(
                    balance=first_create2_value + second_call_value
                )
            else:
                post[create2_address] = Account(
                    balance=first_create2_value, nonce=1, code=initcode.deploy_code
                )
                post[suicide_destination] = Account.NONEXISTENT

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
