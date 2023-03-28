"""
Test EIP-4844: Shard Blob Transactions (DATAHASH Opcode)
EIP: https://eips.ethereum.org/EIPS/eip-4844
"""
from typing import Sequence

from ethereum_test_forks import ShardingFork
from ethereum_test_tools import (
    Account,
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


@test_from(fork=ShardingFork)
def test_datahash_opcode(_: str):
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
def test_datahash_gas(_: str):
    """
    Test DATAHASH opcode gas cost.
    """
    env = Environment(
        coinbase="0x2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
        difficulty=0x20000,
        gas_limit=300000000,
        number=1,
        timestamp=1000,
    )

    datahash_zero_gas_measure_code = CodeGasMeasure(
        code=(Op.PUSH1(0x00) + Op.DATAHASH),
        overhead_cost=3,
        extra_stack_items=1,
    )
    datahash_zero_gas_measure_code_address = to_address(0x100)

    datahash_max_gas_measure_code = CodeGasMeasure(
        code=(Op.PUSH32(2**256 - 1) + Op.DATAHASH),
        overhead_cost=3,
        extra_stack_items=1,
    )
    datahash_max_gas_measure_code_address = to_address(0x200)

    # Store all contracts in pre-state
    pre = {
        TestAddress: Account(balance=1000000000000000000000),
        datahash_zero_gas_measure_code_address: Account(
            code=datahash_zero_gas_measure_code
        ),
        datahash_max_gas_measure_code_address: Account(
            code=datahash_max_gas_measure_code
        ),
    }

    # DATAHASH gas cost on tx type 5
    tx1 = Transaction(
        ty=5,
        nonce=0,
        data=to_hash_bytes(0),
        to=datahash_zero_gas_measure_code_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=[to_hash_bytes(2**256 - 1)],
    )
    tx2 = Transaction(
        ty=5,
        nonce=1,
        data=to_hash_bytes(0),
        to=datahash_max_gas_measure_code_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        max_fee_per_data_gas=10,
        access_list=[],
        blob_versioned_hashes=[to_hash_bytes(2**256 - 1)],
    )

    post = {
        datahash_zero_gas_measure_code_address: Account(
            storage={
                0: DATAHASH_GAS_COST,
            }
        ),
        datahash_max_gas_measure_code_address: Account(
            storage={
                0: DATAHASH_GAS_COST,
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx1, tx2],
        tag="cost_tx_type_5",
    )

    # DATAHASH gas cost on tx type 2
    tx1 = Transaction(
        ty=2,
        nonce=0,
        data=to_hash_bytes(0),
        to=datahash_zero_gas_measure_code_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        access_list=[],
    )

    tx2 = Transaction(
        ty=2,
        nonce=1,
        data=to_hash_bytes(0),
        to=datahash_max_gas_measure_code_address,
        gas_limit=3000000,
        max_fee_per_gas=10,
        max_priority_fee_per_gas=10,
        access_list=[],
    )

    post = {
        datahash_zero_gas_measure_code_address: Account(
            storage={
                0: DATAHASH_GAS_COST,
            }
        ),
        datahash_max_gas_measure_code_address: Account(
            storage={
                0: DATAHASH_GAS_COST,
            }
        ),
    }

    yield StateTest(
        env=env,
        pre=pre,
        post=post,
        txs=[tx1, tx2],
        tag="cost_tx_type_2",
    )
