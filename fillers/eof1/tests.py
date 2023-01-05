"""
EOF tests
"""

from ethereum_test_tools import (
    Account,
    Environment,
    Initcode,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    compute_create2_address,
    compute_create_address,
    test_from,
    to_address,
)

from .code_validation import INVALID as INVALID_CODE
from .code_validation import VALID as VALID_CODE
from .code_validation_jump import INVALID as INVALID_RJUMP
from .code_validation_jump import VALID as VALID_RJUMP
from .container import INVALID as INVALID_CONTAINERS
from .container import VALID as VALID_CONTAINERS

ALL_VALID = VALID_CONTAINERS + VALID_CODE + VALID_RJUMP
ALL_INVALID = INVALID_CONTAINERS + INVALID_CODE + INVALID_RJUMP

EOF_FORK_NAME = "Shanghai"


@test_from(EOF_FORK_NAME)
def test_legacy_initcode_valid_eof_v1_contract(_):
    """
    Test creating various types of valid EOF V1 contracts using legacy
    initcode and a contract creating transaction.
    """
    tx_created_contract = compute_create_address(TestAddress, 0)
    create_opcode_contract = compute_create_address(0x100, 0)

    env = Environment()

    create_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create(0, 0, calldatasize())
            sstore(result, 1)
        }
        """
    )
    create2_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create2(0, 0, calldatasize(), 0)
            sstore(result, 1)
        }
        """
    )

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=0,
        ),
        to_address(0x100): Account(
            code=create_initcode_from_calldata,
        ),
        to_address(0x200): Account(
            code=create2_initcode_from_calldata,
        ),
    }

    post = {
        tx_created_contract: Account(),
        create_opcode_contract: Account(),
    }
    tx_create_contract = Transaction(
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create_opcode = Transaction(
        nonce=1,
        to=to_address(0x100),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create2_opcode = Transaction(
        nonce=2,
        to=to_address(0x200),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    for container in ALL_VALID:
        # print(container.assemble().hex())
        legacy_initcode = Initcode(deploy_code=container)
        tx_create_contract.data = legacy_initcode
        tx_create_opcode.data = legacy_initcode
        tx_create2_opcode.data = legacy_initcode
        post[tx_created_contract].code = container
        post[create_opcode_contract].code = container
        create2_opcode_contract = compute_create2_address(
            0x200, 0, legacy_initcode.assemble()
        )
        post[create2_opcode_contract] = Account(code=container)
        yield StateTest(
            env=env,
            pre=pre,
            post=post,
            txs=[
                tx_create_contract,
                tx_create_opcode,
                tx_create2_opcode,
            ],
            name=container.name
            if container.name is not None
            else "unknown_container",
        )
        del post[create2_opcode_contract]


@test_from(EOF_FORK_NAME)
def test_legacy_initcode_invalid_eof_v1_contract(_):
    """
    Test creating various types of invalid EOF V1 contracts using legacy
    initcode, a contract creating transaction,
    and the CREATE opcode.
    """
    tx_created_contract = compute_create_address(TestAddress, 0)
    create_opcode_contract = compute_create_address(0x100, 0)

    env = Environment()

    create_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create(0, 0, calldatasize())
            sstore(result, 1)
        }
        """
    )
    create2_initcode_from_calldata = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            let result := create2(0, 0, calldatasize(), 0)
            sstore(result, 1)
        }
        """
    )

    pre = {
        TestAddress: Account(
            balance=1000000000000000000000,
            nonce=0,
        ),
        to_address(0x100): Account(
            code=create_initcode_from_calldata,
        ),
        to_address(0x200): Account(
            code=create2_initcode_from_calldata,
        ),
    }

    post = {
        to_address(0x100): Account(
            storage={
                0: 1,
            }
        ),
        tx_created_contract: Account.NONEXISTENT,
        create_opcode_contract: Account.NONEXISTENT,
    }

    tx_create_contract = Transaction(
        nonce=0,
        to=None,
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create_opcode = Transaction(
        nonce=1,
        to=to_address(0x100),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )
    tx_create2_opcode = Transaction(
        nonce=2,
        to=to_address(0x200),
        gas_limit=100000000,
        gas_price=10,
        protected=False,
    )

    for container in ALL_INVALID:
        # print(container.name + ": " + container.assemble().hex())
        legacy_initcode = Initcode(deploy_code=container)
        tx_create_contract.data = legacy_initcode
        tx_create_opcode.data = legacy_initcode
        tx_create2_opcode.data = legacy_initcode
        create2_opcode_contract = compute_create2_address(
            0x200, 0, legacy_initcode.assemble()
        )
        post[create2_opcode_contract] = Account.NONEXISTENT
        yield StateTest(
            env=env,
            pre=pre,
            post=post,
            txs=[
                tx_create_contract,
                tx_create_opcode,
                tx_create2_opcode,
            ],
            name=container.name
            if container.name is not None
            else "unknown_container",
        )
        del post[create2_opcode_contract]
