import pytest

from typing import Optional
from ethereum_test_tools import BlockchainTestFiller, Transaction, Account, TestAddress
from ethereum_test_tools.vm.opcode import Opcodes as Op
from .utils import stride, _state_conversion, accounts, ConversionTx

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7748.md"
REFERENCE_SPEC_VERSION = "TODO"


class StaleAccountTx:
    """
    Class to represent a transaction that modifies an account to be converted, making it completely/partially stale.
    It can be configured to:
    - be in the same block as the conversion transaction or in a previous block
    - revert or not revert
    """

    def __init__(self, same_block_as_conversion: bool, revert: bool):
        self.same_block_as_conversion = same_block_as_conversion
        self.revert = revert


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
@pytest.mark.parametrize(
    "tx_stale_account_config",
    [
        StaleAccountTx(False, False),
        StaleAccountTx(True, False),
        StaleAccountTx(True, True),
    ],
    ids=[
        "Tx generating stale account in previous block",
        "Tx generating stale account in the same block",
        "Reverted tx generating stale account in the same block",
    ],
)
def test_modified_contract(
    blockchain_test: BlockchainTestFiller,
    storage_slot_write: int,
    tx_send_value: bool,
    tx_stale_account_config: StaleAccountTx,
):
    """
    Test converting a modified contract where a previous transaction writes to:
    - Existing storage slots (i.e., storage slots that must not be converted (stale))
    - New storage slots (i.e., storage slots that must not be converted (not overriden with zeros))
    - Basic data (i.e., balance/nonce which must not be converted (stale))
    The conversion transaction can be in the same block or previous block as the conversion.
    """
    _convert_modified_account(
        blockchain_test,
        tx_send_value,
        ContractSetup(storage_slot_write),
        tx_stale_account_config,
    )


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "tx_stale_account_config",
    [
        StaleAccountTx(False, False),
        StaleAccountTx(True, False),
    ],
    ids=[
        "Tx generating stale account in previous block",
        "Tx generating stale account in the same block",
    ],
)
def test_modified_eoa(
    blockchain_test: BlockchainTestFiller, tx_stale_account_config: StaleAccountTx
):
    """
    Test converting a modified EOA in the same block or previous block as the conversion.
    """
    _convert_modified_account(blockchain_test, True, None, tx_stale_account_config)


class ContractSetup:
    def __init__(self, storage_slot_write: Optional[int]):
        self.storage_slot_write = storage_slot_write


def _convert_modified_account(
    blockchain_test: BlockchainTestFiller,
    tx_send_value: bool,
    contract_setup: Optional[ContractSetup],
    tx_stale_account_config: StaleAccountTx,
):
    pre_state = {}
    pre_state[TestAddress] = Account(balance=1000000000000000000000)

    expected_conversion_blocks = 1
    accounts_idx = 0
    if not tx_stale_account_config.same_block_as_conversion:
        expected_conversion_blocks = 2
        # TODO(hack): today the testing-framework does not support us signaling that we want to
        # put the `ConversionTx(tx, **0**)` at the first block after genesis. To simulate that, we have
        # to do this here so we "shift" the target account to the second block in the fork.
        # If this is ever supported, remove this.
        for i in range(stride):
            pre_state[accounts[accounts_idx]] = Account(balance=100 + 1000 * i)
            accounts_idx += 1

    target_account = accounts[accounts_idx]
    if contract_setup is not None:
        pre_state[target_account] = Account(
            balance=1_000,
            nonce=0,
            code=(
                (
                    Op.SSTORE(contract_setup.storage_slot_write, 9999)
                    if contract_setup.storage_slot_write is not None
                    else Op.RETURN
                )
                + Op.REVERT
                if tx_stale_account_config.revert
                else Op.RETURN
            ),
            storage={0: 100, 300: 200},
        )
    else:
        if tx_stale_account_config.revert:
            raise Exception("Invalid test case -- EOA transfers can't revert")
        pre_state[target_account] = Account(balance=10_000, nonce=0)

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        to=target_account,
        value=500 if tx_send_value else 0,
        gas_limit=100_000,
        gas_price=10,
    )

    _state_conversion(
        blockchain_test,
        pre_state,
        stride,
        expected_conversion_blocks,
        [ConversionTx(tx, 0)],
    )


@pytest.mark.valid_from("EIP6800Transition")
def test_modified_eoa_conversion_units(blockchain_test: BlockchainTestFiller):
    """
    Test stale EOA are properly counted as used conversion units.
    """
    pre_state = {}
    pre_state[TestAddress] = Account(balance=1000000000000000000000)

    # TODO(hack): today the testing-framework does not support us signaling that we want to
    # put the `ConversionTx(tx, **0**)` at the first block after genesis. To simulate that, we have
    # to do this here so we "shift" the target account to the second block in the fork.
    # If this is ever supported, remove this.
    for i in range(stride):
        pre_state[accounts[i]] = Account(balance=100 + 1000 * i)

    txs = []
    # Add stride+3 extra EOAs, and invalidate the first stride ones. This is to check that
    # the conversion units are properly counted, and the last 3 aren't converted in that block.
    for i in range(stride + 3):
        pre_state[accounts[stride + i]] = Account(balance=1_000, nonce=0)
        if i < stride:
            tx = Transaction(
                ty=0x0,
                chain_id=0x01,
                nonce=i,
                to=accounts[stride + i],
                value=100,
                gas_limit=100_000,
                gas_price=10,
            )
            txs.append(ConversionTx(tx, 0))

    _state_conversion(blockchain_test, pre_state, stride, 3, txs)


@pytest.mark.valid_from("EIP6800Transition")
def test_modified_contract_conversion_units(blockchain_test: BlockchainTestFiller):
    """
    Test stale contract storage slots are properly counted as used conversion units.
    """
    pre_state = {}
    pre_state[TestAddress] = Account(balance=1000000000000000000000)

    # TODO(hack): today the testing-framework does not support us signaling that we want to
    # put the `ConversionTx(tx, **0**)` at the first block after genesis. To simulate that, we have
    # to do this here so we "shift" the target account to the second block in the fork.
    # If this is ever supported, remove this.
    for i in range(stride):
        pre_state[accounts[i]] = Account(balance=100 + 1000 * i)

    target_account = accounts[stride]
    pre_state[target_account] = Account(
        balance=1_000,
        nonce=0,
        code=sum([Op.SSTORE(ss, 10_000 + i) for i, ss in enumerate(range(stride))]),
        storage={ss: 100 + i for i, ss in enumerate(range(stride))},
    )
    for i in range(3):
        pre_state[accounts[stride + 1 + i]] = Account(balance=1_000 + i, nonce=0)

    # Send tx that writes all existing storage slots.
    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        nonce=0,
        to=target_account,
        value=100,
        gas_limit=100_000,
        gas_price=10,
    )

    _state_conversion(blockchain_test, pre_state, stride, 3, [ConversionTx(tx, 0)])
