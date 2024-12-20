"""
abstract: Tests [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
    Test system contract deployment for [EIP-2935: Serve historical block hashes from state](https://eips.ethereum.org/EIPS/eip-2935)
"""  # noqa: E501

from os.path import realpath
from pathlib import Path

from ethereum_test_forks import Prague
from ethereum_test_tools import Address, generate_system_contract_deploy_test

from .spec import Spec, ref_spec_2935

REFERENCE_SPEC_GIT_PATH = ref_spec_2935.git_path
REFERENCE_SPEC_VERSION = ref_spec_2935.version


@generate_system_contract_deploy_test(
    fork=Prague,
    tx_json_path=Path(realpath(__file__)).parent / "contract_deploy_tx.json",
    expected_deploy_address=Address(Spec.HISTORY_STORAGE_ADDRESS),
    expected_system_contract_storage=None,
)
def test_system_contract_deployment(*args, **kwargs):
    """
    Verify deployment of the block hashes system contract.
    """
    yield from []
