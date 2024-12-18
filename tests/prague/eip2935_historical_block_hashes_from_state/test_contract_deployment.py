"""
abstract: Tests [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
    Test system contract deployment for [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
"""  # noqa: E501

from ethereum_test_forks import Prague
from ethereum_test_tools import Address, generate_system_contract_deploy_test

from .spec import Spec, ref_spec_2935

REFERENCE_SPEC_GIT_PATH = ref_spec_2935.git_path
REFERENCE_SPEC_VERSION = ref_spec_2935.version


@generate_system_contract_deploy_test(
    fork=Prague,
    tx_gas_limit=0x3D090,
    tx_gas_price=0xE8D4A51000,
    tx_init_code=bytes.fromhex(
        "60538060095f395ff33373fffffffffffffffffffffffffffffffffffffffe14604657602036036042575f35"
        "600143038111604257611fff81430311604257611fff9006545f5260205ff35b5f5ffd5b5f35611fff600143"
        "03065500"
    ),
    tx_v=0x1B,
    tx_r=0x539,
    tx_s=0xBAEFE09F0109759,
    expected_deploy_address=Address(Spec.HISTORY_STORAGE_ADDRESS),
    expected_system_contract_storage=None,
)
def test_system_contract_deployment(*args, **kwargs):
    """
    Verify deployment of the block hashes system contract.
    """
    yield from []
