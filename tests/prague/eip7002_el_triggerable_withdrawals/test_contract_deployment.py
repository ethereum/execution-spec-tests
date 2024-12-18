"""
abstract: Tests [EIP-7002: Execution layer triggerable withdrawals](https://eips.ethereum.org/EIPS/eip-7002)
    Test system contract deployment for [EIP-7002: Execution layer triggerable withdrawals](https://eips.ethereum.org/EIPS/eip-7002)
"""  # noqa: E501

from typing import Generator, Tuple

from ethereum_test_forks import Fork, Prague
from ethereum_test_tools import (
    Address,
    Alloc,
    Header,
    Requests,
    Transaction,
    generate_system_contract_deploy_test,
)

from .helpers import WithdrawalRequest
from .spec import Spec, ref_spec_7002

REFERENCE_SPEC_GIT_PATH = ref_spec_7002.git_path
REFERENCE_SPEC_VERSION = ref_spec_7002.version


@generate_system_contract_deploy_test(
    fork=Prague,
    tx_gas_limit=0x3D090,
    tx_gas_price=0xE8D4A51000,
    tx_init_code=bytes.fromhex(
        "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff5f556101f880602d5f395f"
        "f33373fffffffffffffffffffffffffffffffffffffffe1460cb5760115f54807fffffffffffffffffffffff"
        "ffffffffffffffffffffffffffffffffffffffffff146101f457600182026001905f5b5f8211156068578101"
        "9083028483029004916001019190604d565b909390049250505036603814608857366101f457346101f4575f"
        "5260205ff35b34106101f457600154600101600155600354806003026004013381556001015f358155600101"
        "60203590553360601b5f5260385f601437604c5fa0600101600355005b6003546002548082038060101160df"
        "575060105b5f5b8181146101835782810160030260040181604c02815460601b815260140181600101548152"
        "6020019060020154807fffffffffffffffffffffffffffffffff000000000000000000000000000000001682"
        "52906010019060401c908160381c81600701538160301c81600601538160281c81600501538160201c816004"
        "01538160181c81600301538160101c81600201538160081c81600101535360010160e1565b91018092146101"
        "9557906002556101a0565b90505f6002555f6003555b5f54807fffffffffffffffffffffffffffffffffffff"
        "ffffffffffffffffffffffffffff14156101cd57505f5b6001546002828201116101e25750505f6101e8565b"
        "01600290035b5f555f600155604c025ff35b5f5ffd"
    ),
    tx_v=0x1B,
    tx_r=0x539,
    tx_s=0xEB793ED1DCD82833,
    expected_deploy_address=Address(Spec.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS),
    expected_system_contract_storage=None,
)
def test_system_contract_deployment(
    *,
    fork: Fork,
    pre: Alloc,
) -> Generator[Tuple[Transaction, Header], None, None]:
    """
    Verify calling the withdrawals system contract after deployment.
    """
    sender = pre.fund_eoa()
    withdrawal_request = WithdrawalRequest(
        validator_pubkey=0x01,
        amount=1,
        fee=Spec.get_fee(0),
        source_address=sender,
    )
    pre.fund_address(sender, withdrawal_request.value)
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    test_transaction_gas = intrinsic_gas_calculator(calldata=withdrawal_request.calldata)

    test_transaction = Transaction(
        data=withdrawal_request.calldata,
        gas_limit=test_transaction_gas * 10,
        to=Spec.WITHDRAWAL_REQUEST_PREDEPLOY_ADDRESS,
        sender=sender,
        value=withdrawal_request.value,
    )

    yield from [
        (
            test_transaction,
            Header(
                requests_hash=Requests(withdrawal_request),
            ),
        ),
    ]
