"""
abstract: Tests [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685)
    Cross testing for withdrawal and deposit request for [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685)

"""  # noqa: E501

from dataclasses import dataclass
from typing import Dict, List

import pytest

from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    BlockException,
    Environment,
    Header,
)
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    TestAddress,
    TestAddress2,
    TestPrivateKey,
    TestPrivateKey2,
    Transaction,
)

from ..eip6110_deposits.spec import Spec as Spec_EIP6110
from ..eip6110_deposits.test_deposits import (
    DepositContract,
    DepositInteractionBase,
    DepositRequest,
    DepositTransaction,
)
from ..eip7002_el_triggerable_withdrawals.spec import Spec as Spec_EIP7002
from ..eip7002_el_triggerable_withdrawals.test_withdrawal_requests import (
    WithdrawalRequest,
    WithdrawalRequestContract,
    WithdrawalRequestInteractionBase,
    WithdrawalRequestTransaction,
)
from .spec import ref_spec_7685

REFERENCE_SPEC_GIT_PATH = ref_spec_7685.git_path
REFERENCE_SPEC_VERSION = ref_spec_7685.version

pytestmark = pytest.mark.valid_from("Prague")


@dataclass
class SenderAccount:
    """Test sender account descriptor."""

    address: Address
    key: str


TestAccount1 = SenderAccount(TestAddress, TestPrivateKey)
TestAccount2 = SenderAccount(TestAddress2, TestPrivateKey2)

##############
#  Fixtures  #
##############


@pytest.fixture
def pre(
    requests: List[DepositInteractionBase | WithdrawalRequestInteractionBase],
) -> Dict[Address, Account]:
    """
    Initial state of the accounts. Every deposit transaction defines their own pre-state
    requirements, and this fixture aggregates them all.
    """
    pre: Dict[Address, Account] = {}
    for d in requests:
        d.update_pre(pre)
    return pre


@pytest.fixture
def txs(
    requests: List[DepositInteractionBase | WithdrawalRequestInteractionBase],
) -> List[Transaction]:
    """List of transactions to include in the block."""
    address_nonce: Dict[Address, int] = {}
    txs = []
    for r in requests:
        nonce = 0
        if r.sender_account.address in address_nonce:
            nonce = address_nonce[r.sender_account.address]
        txs.append(r.transaction(nonce))
        address_nonce[r.sender_account.address] = nonce + 1
    return txs


@pytest.fixture
def block_body_override_requests() -> List[DepositRequest] | None:
    """List of requests that overwrite the requests in the header. None by default."""
    return None


@pytest.fixture
def exception() -> BlockException | None:
    """Block exception expected by the tests. None by default."""
    return None


@pytest.fixture
def blocks(
    requests: List[DepositInteractionBase | WithdrawalRequestInteractionBase],
    block_body_override_requests: List[DepositRequest | WithdrawalRequest] | None,
    txs: List[Transaction],
    exception: BlockException | None,
) -> List[Block]:
    """List of blocks that comprise the test."""
    included_deposit_requests = []
    included_withdrawal_requests = []
    # Single block therefore base fee
    withdrawal_request_fee = 1
    for r in requests:
        if isinstance(r, DepositInteractionBase):
            included_deposit_requests += r.valid_requests(10**18)
        elif isinstance(r, WithdrawalRequestInteractionBase):
            included_withdrawal_requests += r.valid_requests(withdrawal_request_fee)

    return [
        Block(
            txs=txs,
            header_verify=Header(
                requests_root=included_deposit_requests + included_withdrawal_requests,
            ),
            requests=block_body_override_requests,
            exception=exception,
        )
    ]


################
#  Test cases  #
################


@pytest.mark.parametrize(
    "requests",
    [
        pytest.param(
            [
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
            ],
            id="single_deposit_from_eoa_single_withdrawal_from_eoa",
        ),
        pytest.param(
            [
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
            ],
            id="single_withdrawal_from_eoa_single_deposit_from_eoa",
        ),
        pytest.param(
            [
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x1,
                    ),
                ),
            ],
            id="two_deposits_from_eoa_single_withdrawal_from_eoa",
        ),
        pytest.param(
            [
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=1,
                        fee=1,
                    ),
                ),
            ],
            id="two_withdrawals_from_eoa_single_deposit_from_eoa",
        ),
        pytest.param(
            [
                DepositContract(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
                WithdrawalRequestContract(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
            ],
            id="single_deposit_from_contract_single_withdrawal_from_contract",
        ),
        pytest.param(
            [
                WithdrawalRequestContract(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
                DepositContract(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
            ],
            id="single_withdrawal_from_contract_single_deposit_from_contract",
        ),
        # TODO: Deposit and withdrawal in the same transaction
    ],
)
def test_valid_deposit_withdrawal_requests(
    blockchain_test: BlockchainTestFiller,
    pre: Dict[Address, Account],
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
def test_valid_deposit_withdrawal_request_from_same_tx(
    blockchain_test: BlockchainTestFiller,
    deposit_first: bool,
):
    """
    Test making a deposit to the beacon chain deposit contract and a withdrawal in the same tx.
    """
    contract_address = 0x200
    withdrawal_request_fee = 1
    deposit_request = DepositRequest(
        pubkey=0x01,
        withdrawal_credentials=0x02,
        amount=32_000_000_000,
        signature=0x03,
        index=0x0,
    )
    withdrawal_request = WithdrawalRequest(
        validator_public_key=0x01,
        amount=0,
        source_address=contract_address,
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

    pre = {
        TestAddress: Account(
            balance=10**18,
        ),
        contract_address: Account(
            code=contract_code,
            balance=deposit_request.value + withdrawal_request_fee,
        ),
    }

    tx = Transaction(
        nonce=0,
        gas_limit=1_000_000,
        gas_price=0x07,
        to=contract_address,
        value=0,
        data=calldata,
    )

    block = Block(
        txs=[tx],
        header_verify=Header(
            requests_root=[deposit_request, withdrawal_request],
        ),
    )

    blockchain_test(
        genesis_environment=Environment(),
        pre=pre,
        post={},
        blocks=[block],
    )


@pytest.mark.parametrize(
    "requests,block_body_override_requests,exception",
    [
        pytest.param(
            [
                WithdrawalRequestTransaction(
                    request=WithdrawalRequest(
                        validator_public_key=0x01,
                        amount=0,
                        fee=1,
                    ),
                ),
                DepositTransaction(
                    request=DepositRequest(
                        pubkey=0x01,
                        withdrawal_credentials=0x02,
                        amount=32_000_000_000,
                        signature=0x03,
                        index=0x0,
                    ),
                ),
            ],
            [
                WithdrawalRequest(
                    validator_public_key=0x01,
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
def test_invalid_deposit_withdrawal_requests(
    blockchain_test: BlockchainTestFiller,
    pre: Dict[Address, Account],
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
