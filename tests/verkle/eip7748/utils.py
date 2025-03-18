from ethereum_test_tools.vm.opcode import Opcodes as Op
import math
from ethereum_test_tools import (
    Account,
    Address,
    Block,
    BlockchainTestFiller,
    Transaction,
    Environment,
)

stride = 7

accounts = sorted([Address(i) for i in range(0, 100)], key=lambda x: x.keccak256())


class AccountConfig:
    def __init__(self, code_length: int, storage_slot_count: int):
        self.code_length = code_length
        self.storage_slots_count = storage_slot_count


class StaleBasicDataTx:
    def __init__(self, account_config_idx: int, block_num: int):
        self.account_config_idx = account_config_idx
        self.block_num = block_num


def _generic_conversion(
    blockchain_test: BlockchainTestFiller,
    account_configs: list[AccountConfig],
    fill_first_block: bool,
    fill_last_block: bool,
):
    conversion_units = 0
    pre_state = {}
    account_idx = 0
    if fill_first_block:
        for i in range(stride):
            conversion_units += 1
            pre_state[accounts[account_idx]] = Account(balance=100 + 1000 * i)
            account_idx += 1

    target_accounts: list[Address] = {}
    for i, account_config in enumerate(account_configs):
        storage = {}
        for j in range(account_config.storage_slots_count):
            conversion_units += 1
            storage[j] = j + 1

        pre_state[accounts[account_idx]] = Account(
            balance=100 + 1000 * i,
            nonce=i,
            code=Op.JUMPDEST * account_config.code_length,
            storage=storage,
        )
        target_accounts.append(accounts[account_idx])
        account_idx += 1

        conversion_units += 1  # Account basic data
        num_code_chunks = math.ceil(account_config.code_length / 31)
        # Code is always converted in one go, but it counts for stride quota usage
        conversion_units += min(num_code_chunks, stride - conversion_units % stride)

    if fill_last_block:
        for i in range((-conversion_units) % stride + stride):
            conversion_units += 1
            pre_state[accounts[account_idx]] = Account(balance=100 + 1000 * i)
            account_idx += 1

    _state_conversion(blockchain_test, pre_state, stride, math.ceil(conversion_units / stride))


class ConversionTx:
    def __init__(self, tx: Transaction, block_num: int):
        self.tx = tx
        self.block_num = block_num


def _state_conversion(
    blockchain_test: BlockchainTestFiller,
    pre_state: dict[Address, Account],
    stride: int,
    num_blocks: int,
    txs: list[ConversionTx] = [],
):
    # TODO: test library should allow passing stride
    env = Environment(
        fee_recipient="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=10000000000,
    )

    blocks: list[Block] = []
    for i in range(num_blocks):
        blocks.append(Block(txs=[]))

    for tx in txs:
        blocks[tx.block_num].txs.append(tx.tx)

    # TODO: witness assertion
    # TODO: see if possible last block switch to finished conversion

    blockchain_test(
        genesis_environment=env,
        pre=pre_state,
        post=pre_state.copy(),
        blocks=blocks,
    )
