"""
Test EIP-4200: EOF - Static relative jumps
EIP: https://eips.ethereum.org/EIPS/eip-4200
Source tests: https://github.com/ethereum/tests/pull/1103/
"""

from ethereum_test_tools import (
    Account,
    CodeGasMeasure,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
    to_address,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op


@test_from(fork="shanghai", eips=[4200])
def test_4200_valid(fork):
    """
    Valid EOF RJUMP code
    """
    env = Environment()

    pre = {TestAddress: Account(balance=1000000000000000000000)}
    post = {}

    addr_1 = to_address(0x100)
    addr_2 = to_address(0x200)

    """
    {
        callCODECOPY(0, 0, calldatasize())
        sstore(0, create2(0, 0, calldatasize(), 0))
        sstore(1, 1)
    }
    """
    pre[addr_1] = Account(code=code)
    post[addr_1] = Account(storage={0x00: 0x01})

    # Entry point for all test cases is the same address
    tx = Transaction(
        to=addr_1,
        gas_limit=100000,
    )

    initcode = "ef000101000402000100010300000000000000fe"

    """
    Valid EOF initcode containing RJUMP.
    """
    data = Op.RJUMP(3) + Op.NOP + Op.NOP + Op.RETURN
    data = data + OP.PUSH1(20) + OP.PUSH1(39) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RJUMP(-17)
    data = data + initcode
    tx.data = data
    
    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP"
    )

    """
    Valid EOF initcode containing RJUMP(0).
    """
    data = Op.RJUMP(0) + OP.PUSH1(20) + OP.PUSH1(34) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_0"
    )

    """
    Valid EOF initcode containing RJUMPI positive.
    """
    data = Op.PUSH1(1) + OP.RJUMPI(3) + OP.NOP + OP.NOP + OP.STOP + OP.PUSH1(20) + OP.PUSH1(39) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN 
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPI_pos"
    )

    """
    Valid EOF initcode containing RJUMPI negative.
    """
    data = Op.RJUMP(12) + OP.PUSH1(20) + OP.PUSH1(40) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN + OP.PUSH1(1) + OP.RJUMPI(-17) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPI_neg"
    )

    """
    Valid EOF initcode containing RJUMPI 0.
    """
    data = Op.PUSH1(1) + OP.RJUMPI(0) + OP.PUSH1(20) + OP.PUSH1(36) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPI_zero"
    )

    """
    Valid EOF initcode containing RJUMPV table size 1, positive.
    """
    data = Op.PUSH1(0) + OP.RJUMPV(3) + OP.NOP + OP.NOP + OP.STOP + OP.PUSH1(20) + OP.PUSH1(39) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPV_pos"
    )

    """
    Valid EOF initcode containing RJUMPV table size 1, negative.
    """
    data = Op.RJUMP(12) + OP.PUSH1(20) + OP.PUSH1(41) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN + OP.PUSH1(0) + OP.RJUMPV(-18) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPV_neg"
    )

    """
    Valid EOF initcode containing RJUMPV table size 1, zero.
    """
    data = Op.PUSH1(0) + OP.RJUMPV(0) + OP.PUSH1(20) + OP.PUSH1(37) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPV_zero"
    )

    """
    Valid EOF initcode containing RJUMPV table size 3.
    """
    data = Op.PUSH1(0) + OP.RJUMPV(3, 0, -10) + OP.NOP + OP.NOP + OP.STOP + OP.PUSH1(20) + OP.PUSH1(44) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPV_3"
    )

    """
    Valid EOF initcode containing RJUMPV table size 255.
    """
    data = Op.PUSH1(0) + OP.RJUMPV(255, 0, -10) + OP.NOP + OP.NOP + OP.STOP + OP.PUSH1(20) + OP.PUSH1(44) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(20) + OP.PUSH1(0) + OP.RETURN
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPV_255"
    )

@test_from(fork="shanghai", eips=[4200])
def test_4200_valid(fork):
    """
    Valid EOF RJUMP data
    """
    env = Environment()

    pre = {TestAddress: Account(balance=1000000000000000000000)}
    post = {}

    addr_1 = to_address(0x100)
    addr_2 = to_address(0x200)

    """
    {
        callCODECOPY(0, 0, calldatasize())
        sstore(0, create2(0, 0, calldatasize(), 0))
        sstore(1, 1)
    }
    """
    pre[addr_1] = Account(code=code)
    post[addr_1] = Account(storage={0x00: 0x01})

    # Entry point for all test cases is the same address
    tx = Transaction(
        to=addr_1,
        gas_limit=100000,
    )

    initcode = "ef000101000100FE"

    """
    Invalid EOF Initcode containing containing truncated RJUMP.
    """
    data = Op.PUSH1(8) + OP.PUSH1(23) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN
    data = data + "5c"
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_trunc_1"
    )

    """
    Invalid EOF Initcode containing containing truncated RJUMP.
    """
    data = Op.PUSH1(8) + OP.PUSH1(23) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN
    data = data + "5c00"
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_trunc_2"
    )

    """
    Invalid EOF Initcode containing RJUMP with target outside of code bounds.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(-20) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_invalid_target"
    )

    """
    Jump to before code begin.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(-27) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_before_code"
    )

    """
    Jump into data section.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(2) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_into_data"
    )

    """
    Jump to after code end.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(10) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_after_code"
    )

    """
    Jump to code end.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(1) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_end_code"
    )

    """
    Jump to code end.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(1) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_end_code"
    )


    """
    Invalid EOF Initcode containing RJUMP with target PUSH/RJUMP/RJUMPI immediate.
    """
    
    """
    Jump to same RJUMP immediate.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(-1) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_same_im"
    )

    """
    Jump to another RJUMP immediate.
    """
    data = Op.PUSH1(8) + OP.PUSH1(30) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(1) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_diff_im"
    )

    """
    Jump to RJUMPI immediate.
    """
    data = Op.PUSH1(8) + OP.PUSH1(32) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(2) + OP.STOP + OP.RJUMP(4) + OP.STOP + OP.PUSH1(1) + OP.RJUMPI(-6)
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPI_jump_samr_im"
    )

    """
    Jump to PUSH immediate
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.RJUMP(-5) + OP.STOP
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_push_im"
    )

    """
    Invalid EOF Initcode containing containing truncated RJUMPI.
    """
    data = Op.PUSH1(8) + OP.PUSH1(25) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.PUSH1(1)
    data = data + "5d"
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMPI_truncated"
    )

    """
    Invalid EOF Initcode containing containing truncated RJUMPI.
    """
    data = Op.PUSH1(8) + OP.PUSH1(26) + OP.PUSH1(0) + OP.CODECOPY + OP.PUSH1(8) + OP.PUSH1(0) + OP.RETURN + OP.PUSH1(1)
    data = data + "5d00"
    data = data + initcode
    tx.data = data

    yield StateTest(
        env=env, pre=pre, post=post, txs=[tx], name="EOF_initcode_RJUMP_jump_diff_im"
    )


    """
    Valid EOF Initcode trying to deploy invalid EOF code containing RJUMP with target PUSH/RJUMP/RJUMPI's immediate.
    """
