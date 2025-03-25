"""
abstract: Tests [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685)
    Cross testing for withdrawal and deposit request for [EIP-7685: General purpose execution layer requests](https://eips.ethereum.org/EIPS/eip-7685).

"""  # noqa: E501

from typing import List

from ethereum_test_tools import (
    Account,
    Alloc,
    Block,
    BlockchainTestFiller,
    Transaction,
)
from ethereum_test_types import Requests

from ..eip7002_el_triggerable_withdrawals.helpers import (
    WithdrawalRequest,
    # WithdrawalRequestBase,
    # WithdrawalRequestContract,
    WithdrawalRequestTransaction,
)
from ..eip7002_el_triggerable_withdrawals.spec import Spec as Spec_EIP7002
from .spec import ref_spec_7685

REFERENCE_SPEC_GIT_PATH: str = ref_spec_7685.git_path
REFERENCE_SPEC_VERSION: str = ref_spec_7685.version


# @pytest.mark.parametrize(
#     "requests_list",
#     [
#         WithdrawalRequest(
#             validator_pubkey=0x01,
#             amount=0,
#             fee=Spec_EIP7002.get_fee(0),
#         ),
#         WithdrawalRequest(
#             validator_pubkey=0x01,
#             amount=0,
#             fee=Spec_EIP7002.get_fee(0),
#         ),
#     ],
# )
def test_extra_withdrawals(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    # requests_list: List[WithdrawalRequest],
):
    """Test how clients were to behave when more than 16 withdrawals would be allowed per block."""
    modified_code: bytes = b"3373fffffffffffffffffffffffffffffffffffffffe1460cb5760115f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff146101f457600182026001905f5b5f82111560685781019083028483029004916001019190604d565b909390049250505036603814608857366101f457346101f4575f5260205ff35b34106101f457600154600101600155600354806003026004013381556001015f35815560010160203590553360601b5f5260385f601437604c5fa0600101600355005b6003546002548082038060121160df575060125b5f5b8181146101835782810160030260040181604c02815460601b8152601401816001015481526020019060020154807fffffffffffffffffffffffffffffffff00000000000000000000000000000000168252906010019060401c908160381c81600701538160301c81600601538160281c81600501538160201c81600401538160181c81600301538160101c81600201538160081c81600101535360010160e1565b910180921461019557906002556101a0565b90505f6002555f6003555b5f54807fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff14156101cd57505f5b6001546002828201116101e25750505f6101e8565b01600290035b5f555f600155604c025ff35b5f5ffd"  # noqa: E501
    pre[Spec_EIP7002.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS] = Account(
        code=modified_code,
        nonce=1,
        balance=0,
    )

    # TODO: when i replace the following list with the parameterized version nothing works, why?
    requests_list: List[WithdrawalRequest] = [
        WithdrawalRequest(
            validator_pubkey=0x01,
            amount=0,
            fee=Spec_EIP7002.get_fee(0),
        ),
        WithdrawalRequest(
            validator_pubkey=0x01,
            amount=0,
            fee=Spec_EIP7002.get_fee(0),
        ),
    ]

    # given a list of withdrawal requests construct a withdrawal request transaction
    withdrawal_request_transaction = WithdrawalRequestTransaction(requests=requests_list)
    # prepare withdrawal senders
    withdrawal_request_transaction.update_pre(pre=pre)
    # get transaction list
    txs: List[Transaction] = withdrawal_request_transaction.transactions()

    blockchain_test(
        pre=pre,
        blocks=[
            Block(
                txs=txs,
                # TODO: why do i have to put the first element here to avoid an error? there is more than 1 request per block  # noqa: E501
                requests_hash=Requests(requests_list[0]),
            ),
        ],
        post={},
    )
