"""
Automatically generated opcode tests
"""

from collections import namedtuple
from string import Template

from ethereum_test_tools import (
    Account,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
)

# An opcode in the list, used by several tests
Opcode = namedtuple("Opcode", "text code inps gas")

opcodes = [
    Opcode("stop", "00", 0, 0),
    Opcode("add", "01", 2, 3),
    Opcode("mul", "02", 2, 5),
    Opcode("sub", "03", 2, 3),
    Opcode("div", "04", 2, 5),
    Opcode("sdiv", "05", 2, 5),
    Opcode("mod", "06", 2, 5),
    Opcode("smod", "07", 2, 5),
    Opcode("addmod", "08", 3, 8),
    Opcode("mulmod", "09", 3, 8),
    Opcode("exp", "0a", 2, 10),
    Opcode("signextend", "0b", 2, 5),
    Opcode("lt", "10", 2, 3),
    Opcode("gt", "11", 2, 3),
    Opcode("slt", "12", 2, 3),
    Opcode("sgt", "13", 2, 3),
    Opcode("eq", "14", 2, 3),
    Opcode("iszero", "15", 1, 3),
    Opcode("and", "16", 2, 3),
    Opcode("or", "17", 2, 3),
    Opcode("xor", "18", 2, 3),
    Opcode("not", "19", 1, 3),
    Opcode("shl", "1a", 2, 3),
    Opcode("shr", "1b", 2, 3),
    Opcode("sar", "1c", 2, 3),
    Opcode("sha3", "20", 2, 30),
    Opcode("address", "30", 0, 2),
    Opcode("balance", "31", 1, 100),
    Opcode("origin", "32", 0, 2),
    Opcode("caller", "33", 0, 2),
    Opcode("callvalue", "34", 0, 2),
    Opcode("calldataload", "35", 1, 3),
    Opcode("calldatasize", "36", 0, 2),
    Opcode("calldatacopy", "37", 3, 3),
    Opcode("codesize", "38", 0, 2),
    Opcode("codecopy", "39", 3, 3),
    Opcode("gasprice", "3a", 0, 2),
    Opcode("extcodesize", "3b", 1, 100),
    Opcode("extcodecopy", "3c", 4, 100),
    Opcode("returndatasize", "3d", 0, 2),
    Opcode("returndatacopy", "3e", 3, 3),
    Opcode("extcodehash", "3f", 1, 100),
    Opcode("blockhash", "40", 1, 20),
    Opcode("coinbase", "41", 0, 2),
    Opcode("timestamp", "42", 0, 2),
    Opcode("number", "43", 0, 2),
    Opcode("prevrandao", "44", 0, 2),
    Opcode("gaslimit", "45", 0, 2),
    Opcode("chainid", "46", 0, 2),
    Opcode("selfbalance", "47", 0, 5),
    Opcode("basefee", "48", 0, 2),
    Opcode("pop", "50", 1, 2),
    Opcode("mload", "51", 1, 3 + 3),  # add 3 for allocating memory
    Opcode("mstore", "52", 2, 3 + 3),  # add 3 for allocating memory
    Opcode("mstore8", "53", 2, 3 + 3),  # add 3 for allocating memory
    Opcode(
        "sload", "54", 1, 2100
    ),  # add 2000 for the cost of accessing a cold storage
    Opcode(
        "sstore", "55", 2, 2200
    ),  # add 2000 for the cost of accessing a cold storage
    # JUMP and JUMPI are special cases, because we can't just run them
    Opcode("pc", "58", 0, 2),
    Opcode("msize", "59", 0, 2),
    Opcode("gas", "5a", 0, 2),
    Opcode("nop", "5b", 0, 1),
    # PUSH, DUP, and SWAP are added by software later
    Opcode("log0", "a0", 2, 375),
    Opcode("log1", "a1", 3, 375 * 2),
    Opcode("log2", "a2", 4, 375 * 3),
    Opcode("log3", "a3", 5, 375 * 4),
    Opcode("log4", "a4", 6, 375 * 5),
    Opcode("create", "f0", 3, 32000),
    Opcode("call", "f1", 7, 100),
    Opcode("callcode", "f2", 7, 100),
    Opcode("return", "f3", 2, 0),
    Opcode("delegatecall", "f4", 6, 100),
    Opcode("create2", "f5", 4, 32000),
    Opcode("staticcall", "fa", 6, 100),
    # REVERT and INVALID cannot be checked by this mechanism
    # (they fail, just as underflow does)
]

# Add DUP and SWAP opcodes
for opc in range(1, 17):
    opcodes.append(Opcode("dup" + str(opc), hex(0x80 + opc - 1)[2:], opc, 3))
    opcodes.append(
        Opcode("swap" + str(opc), hex(0x90 + opc - 1)[2:], opc + 1, 3)
    )


# Add PUSH opcodes
for opc in range(1, 33):
    opcodes.append(Opcode("push" + str(opc), hex(0x60 + opc - 1)[2:], 0, 3))


@test_from("london")
def test_bad_opcode(fork):
    """
    Test that the opcodes that should be invalid are invalid
    Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    code_addr = "0x" + "0" * (40 - 4) + "c0de"
    goat_addr = "0x" + "0" * (40 - 4) + "60A7"

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to=code_addr,
        gas_limit=500000,
        gas_price=10,
        protected=False,
    )

    post_valid = {
        code_addr: Account(
            storage={0x00: 1},
        ),
    }

    post_invalid = {
        code_addr: Account(
            storage={0x00: 0},
        ),
    }

    # Check if an Opcode is valid
    def opc_valid(opc):
        """
        Return whether opc will be evaluated as valid by the test or not.
        Note that some opcodes are evaluated as invalid because the way
        they act.
        """
        # PUSH0 is only valid Shanghai and later
        if fork in {"london", "merge"} and opc == 0x5F:
            return False

        # Valid opcodes, but they are terminal, and so cause
        # the SSTORE not to happen
        if opc in {0x00, 0xF3, 0xFD, 0xFF}:
            return False

        # Jumps. If you jump to a random location, you skip the SSTORE
        if opc in {0x56}:
            return False

        # Opcodes that aren't part of a range
        # SHA3
        # STATICCALL
        if opc in {0x20, 0xFA}:
            return True

        # Arithmetic opcodes
        if 0x01 <= opc <= 0x0B:
            return True

        # Logical opcodes
        if 0x10 <= opc <= 0x1D:
            return True

        # Current status opcodes
        if 0x30 <= opc <= 0x48:
            return True

        # Data and state manipulation opcodes
        if 0x50 <= opc <= 0x5B:
            return True

        # Stack manipulation opcodes (SWAP and DUP)
        if 0x5F <= opc <= 0x9F:
            return True

        # LOG opcodes
        if 0xA0 <= opc <= 0xA4:
            return True

        # CALLs and CREATEs
        if 0xF0 <= opc <= 0xF5:
            return True

        return False
        # End of opc_valid

    # For every possible opcode
    for opc in range(256):
        # We can't check SELFDESTRUCT using this technique
        if opc in {0xFF}:
            continue

        opc_hex = hex(opc)[2:]
        # print(fork, opc_hex)
        if len(opc_hex) == 1:
            opc_hex = "0" + opc_hex
        yul_code = Template(
            """
            {
            pop(call(gas(), 0x60A7, 0, 0,0, 0,0))

            // fails on opcodes with >20 inputs
            // (currently dup16, at 17 inputs, is the
            // one that goes deepest)
            //
            // Follow with 32 NOPs (0x5B) to handle PUSH,
            // which has an immediate operand
            verbatim_20i_0o(hex"${opcode}${nops}",
                0x00, 0x00, 0x00, 0xFF, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF)

            // We only get here is the opcode is legit (and it doesn't
            // terminate execution like STOP and RETURN)
            let zero := 0
            let one := 1
            sstore(zero, one)
            }
            """
        ).substitute(opcode=opc_hex, nops="5b" * 32)
        pre = {
            TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
            code_addr: Account(balance=0, nonce=1, code=Yul(yul_code)),
            goat_addr: Account(
                balance=0,
                nonce=1,
                code=Yul("{ return(0,0x100) }"),
            ),
        }
        yield StateTest(
            env=env,
            pre=pre,
            txs=[tx],
            post=post_valid if opc_valid(opc) else post_invalid,
        )


@test_from("berlin")
def test_underflow(fork):
    """
    Test that opcodes underflow when not given enough parameters
    Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    good_addr = "0x" + "0" * (40 - 4) + "600D"
    bad_addr = "0x" + "0" * (40 - 4) + "0BAD"

    pre = {
        "0x1000000000000000000000000000000000000000": Account(
            code=Yul(
                """
                    {
                            sstore(0, call(0x10000, 0x600D, 0, 0,0, 0,0))
                            sstore(1, call(0x10000, 0x0BAD, 0, 0,0, 0,0))
                    }
                """
            ),
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to="0x1000000000000000000000000000000000000000",
        gas_limit=500000,
        gas_price=10,
        protected=False,
    )

    post = {
        "0x1000000000000000000000000000000000000000": Account(
            storage={0x00: 1, 0x01: 0},
        ),
    }

    for opcode in opcodes:
        # print(opcode)
        # If there are no inputs, don't worry about a stack underflow
        if opcode.inps == 0:
            continue

        pre[good_addr] = Account(
            # It has to be zeros, otherwise RETURNDATACOPY fails
            # in the absence of return data
            code="0x"
            + "6000" * opcode.inps
            + opcode.code
            + "00"
        )
        pre[bad_addr] = Account(
            code="0x" + "6000" * (opcode.inps - 1) + opcode.code + "00"
        )

        yield StateTest(env=env, pre=pre, txs=[tx], post=post)


@test_from("merge")
def test_gas_cost(fork):
    """
    Test the gas cost of different opcodes
    Ori Pomerantz qbzzt1@gmail.com
    """
    env = Environment()

    called_addr = "0x" + "0" * (40 - 4) + "600D"

    pre = {
        "0x1000000000000000000000000000000000000000": Account(
            code=Yul(
                """
                    {
                        // Make 0 a warm address
                        pop(call(0x1000, 0, 0, 0,0, 0,0))

                        let b4 := gas()
                        pop(call(0x10000, 0x600D, 0, 0,0, 0,0))
                        sstore(0, sub(b4, gas()))
                    }
                """
            ),
        ),
        TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
    }

    tx = Transaction(
        ty=0x0,
        chain_id=0x0,
        nonce=0,
        to="0x1000000000000000000000000000000000000000",
        gas_limit=500000,
        gas_price=10,
        protected=False,
    )

    for opcode in opcodes:
        # print(opcode)

        post = {
            "0x1000000000000000000000000000000000000000": Account(
                storage={0x00: 2625 + 3 * opcode.inps + opcode.gas},
            ),
        }

        pre[called_addr] = Account(
            # It has to be zeros, otherwise RETURNDATACOPY fails
            # in the absence of return data
            code="0x"
            + "6000" * opcode.inps
            + opcode.code
            + "00"
        )

        yield StateTest(env=env, pre=pre, txs=[tx], post=post)
