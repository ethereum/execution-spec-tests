"""
abstract: Tests [EIP-7251: Increase the MAX_EFFECTIVE_BALANCE](https://eips.ethereum.org/EIPS/eip-7251)
    Test system contract deployment for [EIP-7251: Increase the MAX_EFFECTIVE_BALANCE](https://eips.ethereum.org/EIPS/eip-7251)
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

from .helpers import ConsolidationRequest
from .spec import Spec, ref_spec_7251

REFERENCE_SPEC_GIT_PATH = ref_spec_7251.git_path
REFERENCE_SPEC_VERSION = ref_spec_7251.version


@generate_system_contract_deploy_test(
    fork=Prague,
    tx_gas_limit=0x3D090,
    tx_gas_price=0xE8D4A51000,
    tx_init_code=bytes.fromhex(
        "7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff5f5561019e80602d5f395f"
        "f33373fffffffffffffffffffffffffffffffffffffffe1460d35760115f54807fffffffffffffffffffffff"
        "ffffffffffffffffffffffffffffffffffffffffff1461019a57600182026001905f5b5f8211156068578101"
        "9083028483029004916001019190604d565b9093900492505050366060146088573661019a573461019a575f"
        "5260205ff35b341061019a57600154600101600155600354806004026004013381556001015f358155600101"
        "602035815560010160403590553360601b5f5260605f60143760745fa0600101600355005b60035460025480"
        "82038060021160e7575060025b5f5b8181146101295782810160040260040181607402815460601b81526014"
        "0181600101548152602001816002015481526020019060030154905260010160e9565b910180921461013b57"
        "90600255610146565b90505f6002555f6003555b5f54807fffffffffffffffffffffffffffffffffffffffff"
        "ffffffffffffffffffffffff141561017357505f5b6001546001828201116101885750505f61018e565b0160"
        "0190035b5f555f6001556074025ff35b5f5ffd"
    ),
    tx_v=0x1B,
    tx_r=0x539,
    tx_s=0x332601EF36AA2CE9,
    expected_deploy_address=Address(Spec.CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS),
    expected_system_contract_storage=None,
)
def test_system_contract_deployment(
    *,
    fork: Fork,
    pre: Alloc,
) -> Generator[Tuple[Transaction, Header], None, None]:
    """
    Verify calling the consolidation system contract after deployment.
    """
    sender = pre.fund_eoa()
    consolidation_request = ConsolidationRequest(
        source_pubkey=0x01,
        target_pubkey=0x02,
        fee=Spec.get_fee(0),
        source_address=sender,
    )
    pre.fund_address(sender, consolidation_request.value)
    intrinsic_gas_calculator = fork.transaction_intrinsic_cost_calculator()
    test_transaction_gas = intrinsic_gas_calculator(calldata=consolidation_request.calldata)

    test_transaction = Transaction(
        data=consolidation_request.calldata,
        gas_limit=test_transaction_gas * 10,
        to=Spec.CONSOLIDATION_REQUEST_PREDEPLOY_ADDRESS,
        sender=sender,
        value=consolidation_request.value,
    )

    yield from [
        (
            test_transaction,
            Header(
                requests_hash=Requests(consolidation_request),
            ),
        ),
    ]
