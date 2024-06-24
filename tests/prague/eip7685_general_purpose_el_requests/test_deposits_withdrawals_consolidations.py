"""
abstract: Tests [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685)
    Cross testing for withdrawal and deposit request for [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685)

"""  # noqa: E501

from itertools import permutations
from typing import List

import pytest

from ethereum_test_tools import (
    Alloc,
    Block,
    BlockchainTestFiller,
    BlockException,
    Environment,
    Header,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import TestAddress, Transaction

from ..eip6110_deposits.helpers import DepositContract, DepositRequest, DepositTransaction
from ..eip6110_deposits.spec import Spec as Spec_EIP6110
from ..eip7002_el_triggerable_withdrawals.helpers import (
    WithdrawalRequest,
    WithdrawalRequestContract,
    WithdrawalRequestTransaction,
)
from ..eip7002_el_triggerable_withdrawals.spec import Spec as Spec_EIP7002
from ..eip7251_consolidations.helpers import (
    ConsolidationRequest,
    ConsolidationRequestContract,
    ConsolidationRequestTransaction,
)
from .spec import ref_spec_7685

REFERENCE_SPEC_GIT_PATH = ref_spec_7685.git_path
REFERENCE_SPEC_VERSION = ref_spec_7685.version

pytestmark = pytest.mark.valid_from("Prague")


def single_deposit_from_eoa(i: int) -> DepositTransaction:  # noqa: D103
    return DepositTransaction(
        requests=[
            DepositRequest(
                pubkey=(i * 3),
                withdrawal_credentials=(i * 3) + 1,
                amount=32_000_000_000,
                signature=(i * 3) + 2,
                index=i,
            )
        ],
    )


def single_deposit_from_contract(i: int) -> DepositContract:  # noqa: D103
    return DepositContract(
        requests=[
            DepositRequest(
                pubkey=(i * 3),
                withdrawal_credentials=(i * 3) + 1,
                amount=32_000_000_000,
                signature=(i * 3) + 2,
                index=i,
            )
        ],
    )


def single_withdrawal_from_eoa(i: int) -> WithdrawalRequestTransaction:  # noqa: D103
    return WithdrawalRequestTransaction(
        requests=[
            WithdrawalRequest(
                validator_pubkey=i + 1,
                amount=0,
                fee=1,
            )
        ],
    )


def single_withdrawal_from_contract(i: int) -> WithdrawalRequestContract:  # noqa: D103
    return WithdrawalRequestContract(
        requests=[
            WithdrawalRequest(
                validator_pubkey=i + 1,
                amount=0,
                fee=1,
            )
        ],
    )


def single_consolidation_from_eoa(i: int) -> ConsolidationRequestTransaction:  # noqa: D103
    return ConsolidationRequestTransaction(
        requests=[
            ConsolidationRequest(
                source_pubkey=(i * 2),
                target_pubkey=(i * 2) + 1,
                fee=1,
            )
        ],
    )


def single_consolidation_from_contract(i: int) -> ConsolidationRequestContract:  # noqa: D103
    return ConsolidationRequestContract(
        requests=[
            ConsolidationRequest(
                source_pubkey=(i * 2),
                target_pubkey=(i * 2) + 1,
                fee=1,
            )
        ],
    )


def get_eoa_permutations() -> pytest.param:
    """
    Returns all possible permutations of the requests from an EOA.
    """
    requests = [
        (
            "deposit_from_eoa",
            single_deposit_from_eoa(0),
        ),
        (
            "withdrawal_from_eoa",
            single_withdrawal_from_eoa(0),
        ),
        (
            "consolidation_from_eoa",
            single_consolidation_from_eoa(0),
        ),
    ]
    for perm in permutations(requests, 3):
        yield pytest.param([p[1] for p in perm], id="+".join([p[0] for p in perm]))


def get_contract_permutations() -> pytest.param:
    """
    Returns all possible permutations of the requests from a contract.
    """
    requests = [
        (
            "deposit_from_contract",
            single_deposit_from_contract(0),
        ),
        (
            "withdrawal_from_contract",
            single_withdrawal_from_contract(0),
        ),
        (
            "consolidation_from_contract",
            single_consolidation_from_contract(0),
        ),
    ]
    for perm in permutations(requests, 3):
        yield pytest.param([p[1] for p in perm], id="+".join([p[0] for p in perm]))


@pytest.mark.parametrize(
    "requests",
    [
        *get_eoa_permutations(),
        *get_contract_permutations(),
        pytest.param(
            [
                single_deposit_from_eoa(0),
                single_withdrawal_from_eoa(0),
                single_deposit_from_contract(1),
            ],
            id="deposit_from_eoa+withdrawal_from_eoa+deposit_from_contract",
        ),
        pytest.param(
            [
                single_withdrawal_from_eoa(0),
                single_deposit_from_eoa(0),
                single_withdrawal_from_contract(1),
            ],
            id="withdrawal_from_eoa+deposit_from_eoa+withdrawal_from_contract",
        ),
        pytest.param(
            [
                single_deposit_from_eoa(0),
                single_consolidation_from_eoa(0),
                single_deposit_from_contract(1),
            ],
            id="deposit_from_eoa+consolidation_from_eoa+deposit_from_contract",
        ),
        pytest.param(
            [
                single_consolidation_from_eoa(0),
                single_deposit_from_eoa(0),
                single_consolidation_from_contract(1),
            ],
            marks=pytest.mark.skip("Only one consolidation request is allowed per block"),
            id="consolidation_from_eoa+deposit_from_eoa+consolidation_from_contract",
        ),
        pytest.param(
            [
                single_consolidation_from_eoa(0),
                single_withdrawal_from_eoa(0),
                single_consolidation_from_contract(1),
            ],
            marks=pytest.mark.skip("Only one consolidation request is allowed per block"),
            id="consolidation_from_eoa+withdrawal_from_eoa+consolidation_from_contract",
        ),
        pytest.param(
            [
                single_withdrawal_from_eoa(0),
                single_consolidation_from_eoa(0),
                single_withdrawal_from_contract(1),
            ],
            id="withdrawal_from_eoa+consolidation_from_eoa+withdrawal_from_contract",
        ),
    ],
)
def test_valid_deposit_withdrawal_consolidation_requests(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    blocks: List[Block],
):
    """
    Test making a deposit to the beacon chain deposit contract and a withdrawal in the same block.
    """
    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post={},
        blocks=blocks,
    )


@pytest.mark.parametrize(
    "deposit_first",
    [
        pytest.param(True, id="deposit_first"),
        pytest.param(False, id="withdrawal_first"),
    ],
)
def test_valid_deposit_withdrawal_consolidation_request_from_same_tx(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    deposit_first: bool,
):
    """
    Test making a deposit to the beacon chain deposit contract and a withdrawal in the same tx.
    """
    withdrawal_request_fee = 1
    deposit_request = DepositRequest(
        pubkey=0x01,
        withdrawal_credentials=0x02,
        amount=32_000_000_000,
        signature=0x03,
        index=0x0,
    )
    withdrawal_request = WithdrawalRequest(
        validator_pubkey=0x01,
        amount=0,
    )
    if deposit_first:
        calldata = deposit_request.calldata + withdrawal_request.calldata
        contract_code = (
            Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
            + Op.POP(
                Op.CALL(
                    Op.GAS,
                    Spec_EIP6110.DEPOSIT_CONTRACT_ADDRESS,
                    deposit_request.value,
                    0,
                    len(deposit_request.calldata),
                    0,
                    0,
                )
            )
            + Op.POP(
                Op.CALL(
                    Op.GAS,
                    Spec_EIP7002.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS,
                    withdrawal_request_fee,
                    len(deposit_request.calldata),
                    len(withdrawal_request.calldata),
                    0,
                    0,
                )
            )
        )
    else:
        calldata = withdrawal_request.calldata + deposit_request.calldata
        contract_code = (
            Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
            + Op.POP(
                Op.CALL(
                    Op.GAS,
                    Spec_EIP7002.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS,
                    withdrawal_request_fee,
                    0,
                    len(withdrawal_request.calldata),
                    0,
                    0,
                )
            )
            + Op.POP(
                Op.CALL(
                    Op.GAS,
                    Spec_EIP6110.DEPOSIT_CONTRACT_ADDRESS,
                    deposit_request.value,
                    len(withdrawal_request.calldata),
                    len(deposit_request.calldata),
                    0,
                    0,
                )
            )
        )

    sender = pre.fund_eoa(10**18)
    contract_address = pre.deploy_contract(
        code=contract_code,
        balance=deposit_request.value + withdrawal_request_fee,
    )
    withdrawal_request = withdrawal_request.with_source_address(contract_address)

    tx = Transaction(
        gas_limit=10_000_000,
        to=contract_address,
        value=0,
        data=calldata,
        sender=sender,
    )

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post={},
        blocks=[
            Block(
                txs=[tx],
                header_verify=Header(
                    requests_root=[deposit_request, withdrawal_request],
                ),
            )
        ],
    )


@pytest.mark.parametrize(
    "requests,block_body_override_requests,exception",
    [
        pytest.param(
            [
                WithdrawalRequestTransaction(
                    requests=[
                        WithdrawalRequest(
                            validator_pubkey=0x01,
                            amount=0,
                            fee=1,
                        )
                    ],
                ),
                DepositTransaction(
                    requests=[
                        DepositRequest(
                            pubkey=0x01,
                            withdrawal_credentials=0x02,
                            amount=32_000_000_000,
                            signature=0x03,
                            index=0x0,
                        )
                    ],
                ),
            ],
            [
                WithdrawalRequest(
                    validator_pubkey=0x01,
                    amount=0,
                    source_address=TestAddress,
                ),
                DepositRequest(
                    pubkey=0x01,
                    withdrawal_credentials=0x02,
                    amount=32_000_000_000,
                    signature=0x03,
                    index=0x0,
                ),
            ],
            # TODO: on the Engine API, the issue should be detected as an invalid block hash
            BlockException.INVALID_REQUESTS,
            id="single_deposit_from_eoa_single_withdrawal_from_eoa_incorrect_order",
        ),
    ],
)
def test_invalid_deposit_withdrawal_consolidation_requests(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    blocks: List[Block],
):
    """
    Negative testing for deposits and withdrawals in the same block.
    """
    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post={},
        blocks=blocks,
    )
