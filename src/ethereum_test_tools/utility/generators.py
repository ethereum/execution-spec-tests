"""
Test generator decorators.
"""

from enum import Enum
from typing import Dict, List, Protocol

import pytest

from ethereum_test_base_types import Account, Address
from ethereum_test_forks import Fork
from ethereum_test_specs import BlockchainTestFiller
from ethereum_test_specs.blockchain import Block
from ethereum_test_types import Alloc, Transaction


class SystemContractTestDecoratedFunction(Protocol):
    def __call__(
        self,
        pre: Alloc,
        beacon_root: bytes,
        timestamp: int,
        post: Dict,
        fork: Fork,
    ) -> None:
        ...


def generate_system_contract_deploy_test(
    fork: Fork,
    tx_gas_limit: int,
    tx_gas_price: int,
    tx_init_code: bytes,
    tx_v: int,
    tx_r: int,
    tx_s: int,
    expected_deploy_address: Address,
    expected_system_contract_storage: Dict | None,
    test_transaction_data: bytes,
):
    """
    Decorator to generate a test that verifies the correct deployment of a system contract.

    Generates two tests:
    - One that deploys the contract before the fork.
    - One that deploys the contract after the fork.

    Args:
        fork (Fork): The fork to test.
        tx_gas_limit (int): The gas limit for the deployment transaction.
        tx_gas_price (int): The gas price for the deployment transaction.
        tx_init_code (bytes): The init code for the deployment transaction.
        tx_v (int): The v value for the deployment transaction.
        tx_r (int): The r value for the deployment transaction.
        tx_s (int): The s value for the deployment transaction.
        expected_deploy_address (Address): The expected address of the deployed contract.
        expected_system_contract_storage (Dict): The expected storage of the system contract.
        test_transaction_data (bytes): Data included in the transaction to test the system
            contract deployment.
            Will be executed at the fork block if the deployment is before the fork, or at the
            next block if the deployment is after the fork.
    """

    DeploymentTestType = Enum(
        "DeploymentTestType",
        [
            "DEPLOY_BEFORE_FORK",
            "DEPLOY_AFTER_FORK",
        ],
    )

    def decorator(test_fn):
        @pytest.mark.parametrize(
            "test_type",
            [
                pytest.param(DeploymentTestType.DEPLOY_BEFORE_FORK),
                pytest.param(DeploymentTestType.DEPLOY_AFTER_FORK),
            ],
            ids=lambda x: x.name.lower(),
        )
        @pytest.mark.execute(pytest.mark.skip(reason="modifies pre-alloc"))
        @pytest.mark.valid_at_transition_to(fork.name())
        def wrapper(
            blockchain_test: BlockchainTestFiller,
            pre: Alloc,
            test_type: DeploymentTestType,
            fork: Fork,
        ):
            deployer_required_balance = tx_gas_limit * tx_gas_price
            deploy_tx = Transaction(
                ty=0,
                nonce=0,
                to=None,
                gas_limit=tx_gas_limit,
                gas_price=tx_gas_price,
                value=0,
                data=tx_init_code,
                v=tx_v,
                r=tx_r,
                s=tx_s,
                protected=False,
            ).with_signature_and_sender()
            deployer_address = deploy_tx.sender
            assert deployer_address is not None
            assert deploy_tx.created_contract == expected_deploy_address
            blocks: List[Block] = []

            test_transaction = Transaction(
                data=test_transaction_data,
                to=expected_deploy_address,
                sender=pre.fund_eoa(),
            )

            if test_type == DeploymentTestType.DEPLOY_BEFORE_FORK:
                blocks = [
                    Block(  # Deployment block
                        txs=[deploy_tx],
                        timestamp=14_999,
                    ),
                    Block(  # Contract already deployed
                        txs=[test_transaction],
                        timestamp=15_000,
                    ),
                ]
            elif test_type == DeploymentTestType.DEPLOY_AFTER_FORK:
                blocks = [
                    Block(  # Empty block on fork
                        txs=[],
                        timestamp=15_000,
                    ),
                    Block(  # Deployment block
                        txs=[deploy_tx],
                        timestamp=15_001,
                    ),
                    Block(  # Contract already deployed
                        txs=[test_transaction],
                        timestamp=15_002,
                    ),
                ]

            pre[expected_deploy_address] = Account(
                code=b"",  # Remove the code that is automatically allocated on the fork
                nonce=0,
                balance=0,
            )
            pre[deployer_address] = Account(
                balance=deployer_required_balance,
            )

            post = {}
            fork_pre_allocation = fork.pre_allocation_blockchain()
            assert expected_deploy_address.int() in fork_pre_allocation
            expected_code = fork_pre_allocation[expected_deploy_address.int()]["code"]
            if expected_system_contract_storage is None:
                post[expected_deploy_address] = Account(
                    code=expected_code,
                    nonce=1,
                )
            else:
                post[expected_deploy_address] = Account(
                    storage=expected_system_contract_storage,
                    code=expected_code,
                    nonce=1,
                )
            post[deployer_address] = Account(
                nonce=1,
            )
            blockchain_test(
                pre=pre,
                blocks=blocks,
                post=post,
            )

        return wrapper

    return decorator
