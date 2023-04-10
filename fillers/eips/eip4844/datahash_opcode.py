"""
Test EIP-4844: Shard Blob Transactions (DATAHASH Opcode)
EIP: https://eips.ethereum.org/EIPS/eip-4844
"""
import itertools
import random
from typing import List, Sequence
from string import Template

from ethereum_test_forks import Fork, ShardingFork
from ethereum_test_tools import (
    Account,
    Block,
    BlockchainTest,
    CodeGasMeasure,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    compute_create2_address,
    compute_create_address,
    test_from,
    to_address,
    to_hash_bytes,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4844.md"
REFERENCE_SPEC_VERSION = "b33e063530f0a114635dd4f89d3cca90f8cac28f"

DATAHASH_GAS_COST = 3
MAX_BLOB_PER_BLOCK = 4


@test_from(fork=ShardingFork)
def test_datahash_contexts(_: Fork):
    """
    Test DATAHASH opcode called on different contexts.
    """
    env = Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=300000000,
        number=1,
        timestamp=1000,
    )

    datahash_verbatim = "verbatim_{}i_{}o".format(
        Op.DATAHASH.popped_stack_items, Op.DATAHASH.pushed_stack_items
    )

    datahash_sstore_bytecode = Yul(
        f"""
        {{
           let pos := calldataload(0)
           let end := calldataload(32)
           for {{}} lt(pos, end) {{ pos := add(pos, 1) }}
           {{
            let datahash := {datahash_verbatim}(hex"{Op.DATAHASH.hex()}", pos)
            sstore(pos, datahash)
           }}
           let datahash := {datahash_verbatim}(hex"{Op.DATAHASH.hex()}", end)
           sstore(end, datahash)
           return(0, 0)
        }}
        """
    )
    datahash_sstore_bytecode_address = to_address(0x100)

    datahash_return_bytecode = Yul(
        f"""
        {{
           let pos := calldataload(0)
           let datahash := {datahash_verbatim}(hex"{Op.DATAHASH.hex()}", pos)
           mstore(0, datahash)
           return(0, 32)
        }}
        """
    )
    datahash_return_bytecode_address = to_address(0x600)

    initcode_datahash_sstore_bytecode = Yul(
        f"""
        {{
           for {{ let pos := 0 }} lt(pos, 10) {{ pos := add(pos, 1) }}
           {{
            let datahash := {datahash_verbatim}(hex"{Op.DATAHASH.hex()}", pos)
            sstore(pos, datahash)
           }}
           return(0, 0)
        }}
        """
    )
    tx_created_contract = compute_create_address(TestAddress, 0)

    call_bytecode = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            pop(call(gas(), 0x100, 0, 0, calldatasize(), 0, 0))
        }
        """
    )
    call_bytecode_address = to_address(0x200)

    delegatecall_bytecode = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            pop(delegatecall(gas(), 0x100, 0, calldatasize(), 0, 0))
        }
        """
    )
    delegatecall_bytecode_address = to_address(0x300)

    callcode_bytecode = Yul(
        f"""
{{
    let pos := calldataload(0)
    let end := calldataload(32)
    for {{ }} lt(pos, end) {{ pos := add(pos, 1) }}
    {{
    mstore(0, pos)
    pop(callcode(gas(), {datahash_return_bytecode_address}, 0, 0, 32, 0, 32))
    let datahash := mload(0)
    sstore(pos, datahash)
    }}

    mstore(0, end)
    pop(callcode(gas(), {datahash_return_bytecode_address}, 0, 0, 32, 0, 32))
    let datahash := mload(0)
    sstore(end, datahash)
    return(0, 0)
}}
        """
    )
    callcode_bytecode_address = to_address(0x800)

    staticcall_bytecode = Yul(
        f"""
{{
    let pos := calldataload(0)
    let end := calldataload(32)
    for {{ }} lt(pos, end) {{ pos := add(pos, 1) }}
    {{
    mstore(0, pos)
    pop(staticcall(gas(), {datahash_return_bytecode_address}, 0, 32, 0, 32))
    let datahash := mload(0)
    sstore(pos, datahash)
    }}

    mstore(0, end)
    pop(staticcall(gas(), {datahash_return_bytecode_address}, 0, 32, 0, 32))
    let datahash := mload(0)
    sstore(end, datahash)
    return(0, 0)
}}
        """
    )
    staticcall_bytecode_address = to_address(0x700)

    create_bytecode = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            pop(create(0, 0, calldatasize()))
        }
        """
    )
    create_bytecode_address = to_address(0x400)
    create_opcode_created_contract = compute_create_address(
        create_bytecode_address, 0
    )

    create2_bytecode = Yul(
        """
        {
            calldatacopy(0, 0, calldatasize())
            pop(create2(0, 0, calldatasize(), 0))
        }
        """
    )
    create2_bytecode_address = to_address(0x500)
    create2_opcode_created_contract = compute_create2_address(
        create2_bytecode_address,
        0,
        initcode_datahash_sstore_bytecode.assemble(),
    )

    # Store all contracts in pre-state
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        datahash_sstore_bytecode_address: Account(
            code=datahash_sstore_bytecode
        ),
        call_bytecode_address: Account(code=call_bytecode),
        delegatecall_bytecode_address: Account(code=delegatecall_bytecode),
        create_bytecode_address: Account(code=create_bytecode),
        create2_bytecode_address: Account(code=create2_bytecode),
        datahash_return_bytecode_address: Account(
            code=datahash_return_bytecode
        ),
        staticcall_bytecode_address: Account(code=staticcall_bytecode),
        callcode_bytecode_address: Account(code=callcode_bytecode),
    }

    b_hashes: Sequence[bytes] = [to_hash_bytes(1 << x) for x in range(4)]

    # DATAHASH on top level of the call stack
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(0),
        to=datahash_sstore_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes[:1],
    )

    post = {
        datahash_sstore_bytecode_address: Account(
            storage={
                0: b_hashes[0],
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="at_top_level_call_stack",
    )

    # DATAHASH on max value
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(2**256 - 1) + to_hash_bytes(2**256 - 1),
        to=datahash_sstore_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
    )

    post = {
        datahash_sstore_bytecode_address: Account(storage={}),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="max_value",
    )

    # DATAHASH on CALL
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(1) + to_hash_bytes(1),
        to=call_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes[:2],
        protected=True,
    )
    post = {
        datahash_sstore_bytecode_address: Account(
            storage={
                1: b_hashes[1],
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_call",
    )

    # DATAHASH on DELEGATECALL
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(0) + to_hash_bytes(3),
        to=delegatecall_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        delegatecall_bytecode_address: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_delegatecall",
    )

    # DATAHASH on STATICCALL
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(0) + to_hash_bytes(3),
        to=staticcall_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        staticcall_bytecode_address: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_staticcall",
    )

    # DATAHASH on CALLCODE
    tx = Transaction(
        ty=5,
        data=to_hash_bytes(0) + to_hash_bytes(3),
        to=callcode_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        callcode_bytecode_address: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_staticcall",
    )

    # DATAHASH on Initcode
    tx = Transaction(
        ty=5,
        data=initcode_datahash_sstore_bytecode,
        to=None,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        tx_created_contract: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_initcode",
    )

    # DATAHASH on CREATE
    tx = Transaction(
        ty=5,
        data=initcode_datahash_sstore_bytecode,
        to=create_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        create_opcode_created_contract: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_create",
    )

    # DATAHASH on CREATE2
    tx = Transaction(
        ty=5,
        data=initcode_datahash_sstore_bytecode,
        to=create2_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=b_hashes,
        protected=True,
    )
    post = {
        create2_opcode_created_contract: Account(
            storage={k: v for (k, v) in zip(range(len(b_hashes)), b_hashes)}
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_create2",
    )

    # DATAHASH on tx type == 2
    tx = Transaction(
        ty=2,
        data=to_hash_bytes(0),
        to=datahash_sstore_bytecode_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        access_list=[],
    )

    post = {
        datahash_sstore_bytecode_address: Account(
            storage={
                0: 0,
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_tx_type_2",
    )

    # DATAHASH on tx type == 1
    tx = Transaction(
        ty=1,
        data=to_hash_bytes(0),
        to=datahash_sstore_bytecode_address,
        gas_limit=3000000,
        gas_price=10,
        access_list=[],
    )

    post = {
        datahash_sstore_bytecode_address: Account(
            storage={
                0: 0,
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_tx_type_1",
    )

    # DATAHASH on tx type == 0
    tx = Transaction(
        ty=0,
        data=to_hash_bytes(0),
        to=datahash_sstore_bytecode_address,
        gas_limit=3000000,
        gas_price=10,
    )

    post = {
        datahash_sstore_bytecode_address: Account(
            storage={
                0: 0,
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx],
        tag="on_tx_type_0",
    )


@test_from(fork=ShardingFork)
def test_datahash_gas_cost(_: Fork):
    """
    Test DATAHASH opcode gas cost using a variety of indexes.
    """

    env = Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=300000000,
        number=1,
        timestamp=1000,
    )

    # Initial measures with zero, random and max values
    gas_measures: List[int] = [
        0x00,
        2**3 - 1,
        2**13,
        2**51 - 1,
        2**47,
        2**82 - 1,
        2**115,
        2**152 - 1,
        2**190,
        2**229 - 1,
        2**256 - 1,
    ]

    gas_measures_code = [
        CodeGasMeasure(
            code=Op.PUSH32(gas_measure) + Op.DATAHASH,
            overhead_cost=3,
            extra_stack_items=1,
        )
        for gas_measure in gas_measures
    ]

    pre = {
        TestAddress: Account(balance=1000000000000000000000),
    }
    post = {}

    # Transaction template
    tx = Transaction(
        data=to_hash_bytes(0),
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_fee_per_data_gas=10,
    )

    txs_ty0, txs_ty1, txs_ty2, txs_ty5 = ([] for _ in range(4))
    for i, code_gas_measure in enumerate(gas_measures_code):
        address = to_address(0x100 + i * 0x100)
        pre[address] = Account(code=code_gas_measure)
        post[address] = Account(storage={0: DATAHASH_GAS_COST})
        txs_ty0.append(tx.with_fields(ty=0, to=address, nonce=i, gas_price=10))
        txs_ty1.append(tx.with_fields(ty=1, to=address, nonce=i, gas_price=10))
        txs_ty2.append(
            tx.with_fields(
                ty=2, to=address, nonce=i, max_priority_fee_per_gas=10
            )
        )
        txs_ty5.append(
            tx.with_fields(
                ty=5,
                to=address,
                nonce=i,
                max_priority_fee_per_gas=10,
                blob_versioned_hashes=[to_hash_bytes(2**256 - 1)],
            )
        )

    # DATAHASH gas cost on tx type 0 to 2
    for i, txs in enumerate([txs_ty0, txs_ty1, txs_ty2]):
        yield StateTest(
            env=env, pre=pre, post=post, txs=txs, tag=f"tx_type_{i}"
        )

    # DATAHASH gas cost on tx type 5
    num_blocks = (len(txs_ty5) + MAX_BLOB_PER_BLOCK - 1) // MAX_BLOB_PER_BLOCK
    blocks = [
        Block(
            txs=txs_ty5[i * MAX_BLOB_PER_BLOCK : (i + 1) * MAX_BLOB_PER_BLOCK]
        )
        for i in range(num_blocks)
    ]

    yield BlockchainTest(pre=pre, post=post, blocks=blocks, tag="tx_type_5")


@test_from(fork=ShardingFork)
def test_datahash_blob_versioned_hash(_: Fork):
    """
    Tests that the `DATAHASH` opcode returns the correct versioned hash for
    various valid index scenarios.
    """
    NUM_BLOCKS = 10

    pre = {
        TestAddress: Account(balance=10000000000000000000000),
    }
    post = {}
    blocks = []

    # Create an arbitrary repeated list of blob hashes
    # with length MAX_BLOB_PER_BLOCK * NUM_BLOCKS
    blob_ver_hashes = list(
        itertools.islice(
            itertools.cycle(
                [
                    to_hash_bytes(value)
                    for value in [
                        MAX_BLOB_PER_BLOCK,
                        2**3 - 1,
                        2**13,
                        2**51 - 1,
                        2**47,
                        2**82 - 1,
                        2**115,
                        2**152 - 1,
                        2**190,
                        2**229 - 1,
                        2**239,
                        2**256 - 1,
                    ]
                ]
            ),
            MAX_BLOB_PER_BLOCK * NUM_BLOCKS,
        )
    )

    # `DATAHASH` sstore template helper
    def datahash_sstore(index: int):
        return Op.PUSH1(index) + Op.DATAHASH + Op.PUSH1(index) + Op.SSTORE()

    # `DATAHASH` on valid indexes
    datahash_single_valid_calls = b"".join(
        datahash_sstore(i) for i in range(MAX_BLOB_PER_BLOCK)
    )
    pre_single_valid_calls = pre

    # `DATAHASH` on valid index repeated:
    # DATAHASH(i), DATAHASH(i), ...
    datahash_repeated_valid_calls = b"".join(
        b"".join([datahash_sstore(i) for _ in range(10)])
        for i in range(MAX_BLOB_PER_BLOCK)
    )
    pre_datahash_repeated_valid_calls = pre

    # `DATAHASH` on valid/invalid/valid:
    # DATAHASH(i), DATAHASH(MAX_BLOB_PER_BLOCK), DATAHASH(i)
    datahash_valid_invalid_calls = b"".join(
        datahash_sstore(i)
        + datahash_sstore(MAX_BLOB_PER_BLOCK)
        + datahash_sstore(i)
        for i in range(MAX_BLOB_PER_BLOCK)
    )
    pre_datahash_valid_invalid_calls = pre

    # `DATAHASH` on diffent valid indexes repeated:
    # DATAHASH(i), DATAHASH(i+1), DATAHASH(i)
    datahash_varied_valid_calls = b"".join(
        datahash_sstore(i) + datahash_sstore(i + 1) + datahash_sstore(i)
        for i in range(MAX_BLOB_PER_BLOCK - 1)
    )
    pre_datahash_varied_valid_calls = pre

    for i in range(NUM_BLOCKS):
        address = to_address(0x100 + i * 0x100)
        pre_single_valid_calls[address] = Account(
            code=datahash_single_valid_calls
        )
        pre_datahash_repeated_valid_calls[address] = Account(
            code=datahash_repeated_valid_calls
        )
        pre_datahash_valid_invalid_calls[address] = Account(
            code=datahash_valid_invalid_calls
        )
        pre_datahash_varied_valid_calls[address] = Account(
            code=datahash_varied_valid_calls
        )
        blocks.append(
            Block(
                txs=[  # Create tx with max blobs per block
                    Transaction(
                        ty=5,
                        nonce=i,
                        data=to_hash_bytes(0),
                        to=address,
                        gas_limit=3000000,
                        max_fee_per_gas=10,
                        max_priority_fee_per_gas=10,
                        max_fee_per_data_gas=10,
                        access_list=[],
                        blob_versioned_hashes=blob_ver_hashes[
                            (i * MAX_BLOB_PER_BLOCK) : (i + 1)
                            * MAX_BLOB_PER_BLOCK
                        ],
                    )
                ]
            )
        )
        post[address] = Account(
            storage={
                index: blob_ver_hashes[i * MAX_BLOB_PER_BLOCK + index]
                for index in range(MAX_BLOB_PER_BLOCK)
            }
        )

    yield BlockchainTest(
        pre=pre_single_valid_calls,
        post=post,
        blocks=blocks,
        tag="valid_calls",
    )

    yield BlockchainTest(
        pre=pre_datahash_repeated_valid_calls,
        post=post,
        blocks=blocks,
        tag="repeated_calls",
    )

    yield BlockchainTest(
        pre=pre_datahash_valid_invalid_calls,
        post=post,
        blocks=blocks,
        tag="valid_invalid_calls",
    )

    yield BlockchainTest(
        pre=pre_datahash_varied_valid_calls,
        post=post,
        blocks=blocks,
        tag="valid_invalid_calls",
    )


@test_from(fork=ShardingFork)
def test_datahash_invalid_blob_index(_: Fork):
    """
    Tests that the `DATAHASH` opcode returns a zeroed bytes32 value
    for invalid indexes.
    """

    INVALID_DEPTH = 5
    NUM_BLOCKS = 10

    pre = {
        TestAddress: Account(balance=10000000000000000000000),
    }
    blocks = []
    post = {}

    datahash_verbatim = "verbatim_{}i_{}o".format(
        Op.DATAHASH.popped_stack_items, Op.DATAHASH.pushed_stack_items
    )

    # Start from -INVALID_DEPTH to (${num_blobs} + INVALID_DEPTH)
    datahash_invalid_index_code = Template(
        f"""
        {{
            let pos := 0
            let relative_pos := sub(0, {INVALID_DEPTH})
            let end := add(${{num_blobs}}, {INVALID_DEPTH})
            for {{}} lt(pos, end) {{ pos := add(pos, 1) }}
            {{
                let adjusted_pos := add(pos, relative_pos)
                let datahash := {datahash_verbatim}(
                    hex"{Op.DATAHASH.hex()}", adjusted_pos
                )
                sstore(adjusted_pos, datahash)
            }}
        }}
        """
    )

    for i in range(NUM_BLOCKS):
        address = to_address(0x100 + i * 0x100)
        rnd_blob_size = random.randint(0, MAX_BLOB_PER_BLOCK)
        pre[address] = Account(
            code=Yul(
                datahash_invalid_index_code.substitute(num_blobs=rnd_blob_size)
            )
        )
        blob_ver_hashes = [
            to_hash_bytes(random.randint(MAX_BLOB_PER_BLOCK, 2**256 - 1))
            for _ in range(rnd_blob_size)
        ]
        blocks.append(
            Block(
                txs=[  # Create tx with rnd num valid blobs per block
                    Transaction(
                        ty=5,
                        nonce=i,
                        data=to_hash_bytes(0),
                        to=address,
                        gas_limit=3000000,
                        max_fee_per_gas=10,
                        max_priority_fee_per_gas=10,
                        max_fee_per_data_gas=10,
                        access_list=[],
                        blob_versioned_hashes=blob_ver_hashes,
                    )
                ]
            )
        )
        post[address] = Account(
            storage={
                index: 0
                if index < 0 or index >= rnd_blob_size
                else blob_ver_hashes[index]
                for index in range(
                    -INVALID_DEPTH, rnd_blob_size + INVALID_DEPTH
                )
            }
        )

    yield BlockchainTest(
        pre=pre,
        post=post,
        blocks=blocks,
    )
