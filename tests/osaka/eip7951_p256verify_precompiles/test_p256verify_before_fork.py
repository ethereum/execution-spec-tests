"""
abstract: Tests P256VERIFY precompiles of [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)
    Tests P256VERIFY precompiles of [EIP-7951: Precompile for secp256r1 Curve Support](https://eips.ethereum.org/EIPS/eip-7951)
    before the Osaka hard fork is active.
"""

import pytest

from ethereum_test_tools import Alloc, Block, BlockchainTestFiller, Transaction

from .spec import Spec, ref_spec_7951

REFERENCE_SPEC_GIT_PATH = ref_spec_7951.git_path
REFERENCE_SPEC_VERSION = ref_spec_7951.version

pytestmark = pytest.mark.valid_at_transition_to("Osaka")


@pytest.mark.parametrize(
    "precompile_address,input_data",
    [
        pytest.param(
            Spec.P256VERIFY,
            Spec.H0 + Spec.R0 + Spec.S0 + Spec.X0 + Spec.Y0,
            id="P256VERIFY",
        ),
    ],
)
@pytest.mark.parametrize(
    "expected_output,call_succeeds", [pytest.param(b"", True, id=pytest.HIDDEN_PARAM)]
)
@pytest.mark.eip_checklist("precompile/test/fork_transition/before/invalid_input")
def test_precompile_before_fork(
    blockchain_test: BlockchainTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """
    Test P256VERIFY precompiles before the Osaka hard fork is active.

    The call must succeed but the output must be empty.
    """
    blockchain_test(
        pre=pre,
        blocks=[Block(txs=[tx])],
        post=post,
    )
