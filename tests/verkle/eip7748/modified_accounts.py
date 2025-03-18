import pytest

from typing import Optional
from ethereum_test_tools import BlockchainTestFiller, Transaction, Account, TestAddress
from ethereum_test_tools.vm.opcode import Opcodes as Op
from .utils import stride, _state_conversion, accounts, ConversionTx

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7748.md"
REFERENCE_SPEC_VERSION = "TODO"


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "storage_slot_write",
    [
        None,
        0,
        1,
        300,
        301,
    ],
    ids=[
        "No storage slot modified",
        "Stale storage slot in the header",
        "New storage slot in the account header",
        "Stale storage slot outside the header",
        "New storage slot outside the header",
    ],
)
@pytest.mark.parametrize(
    "tx_send_value",
    [True, False],
)
def test_modified_contract(
    blockchain_test: BlockchainTestFiller,
    storage_slot_write: int,
    tx_send_value: bool,
):
    """
    Test converting a modified contract where a previous transaction writes to:
    - Existing storage slots (i.e., storage slots that must not be converted (stale))
    - New storage slots (i.e., storage slots that must not be converted (not overriden with zeros))
    - Basic data (i.e., balance/nonce which must not be converted (stale))
    """
    _convert_modified_account(blockchain_test, tx_send_value, ContractSetup(storage_slot_write))


@pytest.mark.valid_from("EIP6800Transition")
def test_modified_eoa(
    blockchain_test: BlockchainTestFiller,
):
    """
    Test converting a modified EOA.
    """
    _convert_modified_account(blockchain_test, True, None)


class ContractSetup:
    def __init__(self, storage_slot_write: Optional[int]):
        self.storage_slot_write = storage_slot_write


def _convert_modified_account(
    blockchain_test: BlockchainTestFiller,
    tx_send_value: bool,
    contract_setup: Optional[ContractSetup],
):
    pre_state = {}
    pre_state[TestAddress] = Account(balance=1000000000000000000000)

    # TODO(hack): today the testing-framework does not support us signaling that we want to
    # put the `ConversionTx(tx, **0**)` at the first block after genesis. To simulate that, we have
    # to do this here so we "shift" the target account to the second block in the fork.
    # If this is ever supported, remove this.
    for i in range(stride):
        pre_state[accounts[i]] = Account(balance=100 + 1000 * i)

    target_account = accounts[stride]
    if contract_setup is not None:
        pre_state[target_account] = Account(
            balance=1_000,
            nonce=0,
            code=(
                Op.SSTORE(contract_setup.storage_slot_write, 9999)
                if contract_setup.storage_slot_write is not None
                else []
            ),
            storage={0: 100, 300: 200},
        )
    else:
        pre_state[target_account] = Account(balance=1_000, nonce=0)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        to=target_account,
        value=100 if tx_send_value else 0,
        gas_limit=100_000,
        gas_price=10,
    )

    _state_conversion(blockchain_test, pre_state, stride, 1, [ConversionTx(tx, 0)])
