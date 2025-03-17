"""Check T8N filling support."""

from typing import Dict, Generator

import pytest

from ethereum_clis import (
    BesuTransitionTool,
    ExecutionSpecsTransitionTool,
    TransitionTool,
)
from ethereum_test_base_types import Account, Address, TestAddress, TestPrivateKey
from ethereum_test_forks import (
    ArrowGlacier,
    Berlin,
    Byzantium,
    Cancun,
    Constantinople,
    Fork,
    GrayGlacier,
    London,
    MuirGlacier,
    Paris,
    Prague,
    get_deployed_forks,
)
from ethereum_test_specs.blockchain import BlockchainFixture, BlockchainTest
from ethereum_test_tools import (
    AccessList,
    AuthorizationTuple,
    Block,
    Environment,
    Storage,
    Transaction,
    Withdrawal,
    add_kzg_version,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types import Alloc

BLOB_COMMITMENT_VERSION_KZG = 1

fork_set = set(get_deployed_forks())
fork_set.add(Prague)

test_transition_tools = [
    transition_tool
    for transition_tool in TransitionTool.registered_tools
    if (
        transition_tool.is_installed()
        # Currently, Besu has the same `default_binary` as Geth, so we can't test filling
        and transition_tool != BesuTransitionTool
    )
]


@pytest.fixture(scope="session")
def all_t8n_instances() -> Generator[Dict[str, TransitionTool | Exception], None, None]:
    """Return all instantiated transition tools."""
    t8n_instances: Dict[str, TransitionTool | Exception] = {}
    for t8n_class in test_transition_tools:
        try:
            instantiated_class = t8n_class()
            t8n_instances[t8n_class.__name__] = instantiated_class
        except Exception as e:
            # Record the exception in order to provide context when failing the appropriate test
            t8n_instances[t8n_class.__name__] = e
    yield t8n_instances
    for t8n_instance in t8n_instances.values():
        if isinstance(t8n_instance, TransitionTool):
            t8n_instance.shutdown()


@pytest.fixture
def t8n(
    request: pytest.FixtureRequest, all_t8n_instances: Dict[str, TransitionTool | Exception]
) -> TransitionTool:
    """Return an instantiated transition tool."""
    t8n_class = request.param
    assert issubclass(t8n_class, TransitionTool)
    assert t8n_class.__name__ in all_t8n_instances, f"{t8n_class.__name__} not instantiated"
    t8n_instance_or_error = all_t8n_instances[t8n_class.__name__]
    if isinstance(t8n_instance_or_error, Exception):
        raise Exception(f"Failed to instantiate {t8n_class.__name__}") from t8n_instance_or_error
    return t8n_instance_or_error


@pytest.mark.parametrize("fork", sorted(fork_set, key=lambda f: f.__name__))  # type: ignore
@pytest.mark.parametrize(
    "t8n",
    test_transition_tools,
    indirect=True,
)
def test_t8n_support(fork: Fork, t8n: TransitionTool):
    """Stress test that sends all possible t8n interactions."""
    if fork in [MuirGlacier, ArrowGlacier, GrayGlacier]:
        return
    if isinstance(t8n, ExecutionSpecsTransitionTool) and fork in [Constantinople]:
        return
    env = Environment()
    sender = TestAddress
    storage_1 = Storage()
    storage_2 = Storage()

    code_account_1 = Address(0x1001)
    code_account_2 = Address(0x1002)
    pre = Alloc(
        {
            TestAddress: Account(balance=10_000_000),
            code_account_1: Account(
                code=Op.SSTORE(
                    storage_1.store_next(1, "blockhash_0_is_set"), Op.GT(Op.BLOCKHASH(0), 0)
                )
                + Op.SSTORE(storage_1.store_next(0, "blockhash_1"), Op.BLOCKHASH(1))
                + Op.SSTORE(
                    storage_1.store_next(1 if fork < Paris else 0, "difficulty_1_is_near_20000"),
                    Op.AND(Op.GT(Op.PREVRANDAO(), 0x19990), Op.LT(Op.PREVRANDAO(), 0x20100)),
                )
            ),
            code_account_2: Account(
                code=Op.SSTORE(
                    storage_2.store_next(1, "blockhash_1_is_set"), Op.GT(Op.BLOCKHASH(1), 0)
                )
                + Op.SSTORE(
                    storage_2.store_next(1 if fork < Paris else 0, "difficulty_2_is_near_20000"),
                    Op.AND(Op.GT(Op.PREVRANDAO(), 0x19990), Op.LT(Op.PREVRANDAO(), 0x20100)),
                )
            ),
        }
    )

    tx_1 = Transaction(
        gas_limit=100_000,
        to=code_account_1,
        data=b"",
        nonce=0,
        secret_key=TestPrivateKey,
        protected=fork >= Byzantium,
    )
    if fork < Berlin:
        # Feed legacy transaction, type 0
        tx_2 = Transaction(
            gas_limit=100_000,
            to=code_account_2,
            data=b"",
            nonce=1,
            secret_key=TestPrivateKey,
            protected=fork >= Byzantium,
        )
    elif fork < London:
        # Feed access list transaction, type 1
        tx_2 = Transaction(
            gas_limit=100_000,
            to=code_account_2,
            data=b"",
            nonce=1,
            secret_key=TestPrivateKey,
            protected=fork >= Byzantium,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    elif fork < Cancun:
        # Feed base fee transaction, type 2
        tx_2 = Transaction(
            to=code_account_2,
            data=b"",
            nonce=1,
            secret_key=TestPrivateKey,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    elif fork < Prague:
        # Feed blob transaction, type 3
        tx_2 = Transaction(
            to=code_account_2,
            data=b"",
            nonce=1,
            secret_key=TestPrivateKey,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            max_fee_per_blob_gas=30,
            blob_versioned_hashes=add_kzg_version([1], BLOB_COMMITMENT_VERSION_KZG),
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
        )
    else:
        # Feed set code transaction, type 4
        tx_2 = Transaction(
            to=sender,
            data=b"",
            sender=sender,
            secret_key=TestPrivateKey,
            protected=fork >= Byzantium,
            gas_limit=100_000,
            max_priority_fee_per_gas=5,
            max_fee_per_gas=10,
            nonce=1,
            access_list=[
                AccessList(
                    address=0x1234,
                    storage_keys=[0, 1],
                )
            ],
            authorization_list=[
                AuthorizationTuple(
                    address=code_account_2, nonce=2, signer=sender, secret_key=TestPrivateKey
                ),
            ],
        )

    block_1 = Block(
        txs=[tx_1],
        expected_post_state={
            code_account_1: Account(
                storage=storage_1,
            ),
        },
    )

    block_2 = Block(
        txs=[tx_2],
        expected_post_state={
            code_account_2: Account(
                balance=1_000_000_000 if fork >= Cancun else 0,
                storage=storage_2,
            ),
        }
        if fork < Prague
        else {
            code_account_2: Account(
                balance=1_000_000_000 if fork >= Cancun else 0,
            ),
            sender: Account(
                storage=storage_2,
            ),
        },
    )

    if fork >= Cancun:
        block_2.withdrawals = [
            Withdrawal(
                address=code_account_2,
                amount=1,
                index=1,
                validator_index=0,
            ),
        ]

    test = BlockchainTest(
        genesis_environment=env,
        pre=pre,
        post=block_1.expected_post_state,
        blocks=[block_1, block_2],
    )
    test.generate(
        request=None,  # type: ignore
        t8n=t8n,
        fork=fork,
        fixture_format=BlockchainFixture,
    )
