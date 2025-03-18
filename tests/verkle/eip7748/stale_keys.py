import pytest

from ethereum_test_tools import BlockchainTestFiller, Transaction, Account, TestAddress
from ethereum_test_tools.vm.opcode import Opcodes as Op
from .utils import stride, _state_conversion, accounts, ConversionTx

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-7748.md"
REFERENCE_SPEC_VERSION = "TODO"


@pytest.mark.valid_from("EIP6800Transition")
@pytest.mark.parametrize(
    "storage_slot_write",
    [
        0,
        1,
        300,
        301,
    ],
    ids=[
        "Stale storage slot in the header",
        "New storage slot in the account header",
        "Stale storage slot outside the header",
        "New storage slot outside the header",
    ],
)
@pytest.mark.parametrize(
    "stale_basic_data",
    [True, False],
)
def test_stale_contract_writes(
    blockchain_test: BlockchainTestFiller,
    storage_slot_write: int,
    stale_basic_data: bool,
):
    """
    Test converting a contract where a previous transaction writes to:
    - Existing storage slots (i.e., storage slots that must not be converted (stale))
    - New storage slots (i.e., storage slots that must not be converted (not overriden with zeros))
    - Basic data (i.e., balance/nonce which must not be converted (stale))
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
        code=Op.SSTORE(storage_slot_write, 9999),
        storage={
            0: 100,
            300: 200,
        },
    )

    tx = Transaction(
        ty=0x0,
        chain_id=0x01,
        to=target_account,
        value=100 if stale_basic_data else 0,
        gas_limit=100_000,
        gas_price=10,
    )

    _state_conversion(blockchain_test, pre_state, stride, 1, [ConversionTx(tx, 0)])


# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "num_storage_slots, num_stale_storage_slots",
#     [
#         (0, 0),
#         (4, 0),
#         (4, 2),
#         (stride, stride),
#     ],
#     ids=[
#         "EOA",
#         "Contract without stale storage",
#         "Contract with some stale storage",
#         "Contract with all stale storage",
#     ],
# )
# @pytest.mark.parametrize(
#     "stale_basic_data",
#     [True, False],
# )
# @pytest.mark.parametrize(
#     "fill_first_block",
#     [True, False],
# )
# @pytest.mark.parametrize(
#     "fill_last_block",
#     [True, False],
# )
# def test_stale_keys(
#     blockchain_test: BlockchainTestFiller,
#     account_configs: list[AccountConfig],
#     fill_first_block: bool,
#     fill_last_block: bool,
# ):
#     """
#     Test account conversion with full/partial stale storage slots and basic data.
#     """
#     _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)


# @pytest.mark.valid_from("EIP6800Transition")
# @pytest.mark.parametrize(
#     "fill_first_block",
#     [True, False],
# )
# @pytest.mark.parametrize(
#     "fill_last_block",
#     [True, False],
# )
# def test_stride_stale_eoas(
#     blockchain_test: BlockchainTestFiller,
#     account_configs: list[AccountConfig],
#     fill_first_block: bool,
#     fill_last_block: bool,
# ):
#     """
#     Test converting a stride number of stale EOAs.
#     """
#     _generic_conversion(blockchain_test, account_configs, fill_first_block, fill_last_block)
