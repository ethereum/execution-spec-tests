"""
Automatically generated opcode tests
Ori Pomerantz qbzzt1@gmail.com
"""

from ethereum_test_tools import (
    Account,
    Environment,
    StateTest,
    TestAddress,
    Transaction,
    Yul,
    test_from,
)

from string import Template





@test_from("london")
def test_bad_opcode(fork):
    """
    Test that the opcodes that should be invalid are invalid
    """
    env = Environment()

    codeAddr = "0x" + "0"*(40-4) + "c0de"
    goatAddr = "0x" + "0"*(40-4) + "60A7"

    tx = Transaction(
           ty=0x0,
           chain_id=0x0,
           nonce=0,
           to=codeAddr,
           gas_limit=500000,
           gas_price=10,
           protected=False,
        )

    postValid = {
       codeAddr: Account(
         storage={0x00: 1},
       ),
    }

    postInvalid = {
       codeAddr: Account(
         storage={0x00: 0},
       ),
    }

    # Check if an Opcode is valid
    def opcValid(opc):
        """
        Return whether opc will be evaluated as valid by the test or not.
        Note that some opcodes are evaluated as invalid because the way they act
        """

        # PUSH0 is only valid Shanghai and later
        if fork in {"london", "merge"} and opc==0x5F:
            return False

        # Valid opcodes, but they are terminal, and so cause
        # the SSTORE not to happen
        if opc in {0x00, 0xF3, 0xFD, 0xFF}:
            return False

        # Jumps. If you jump to a random location, you skip the SSTORE
        if opc in {0x56}:
            return False

        # Opcodes that aren't part of a range
        # 0x20 - SHA3
        # 0xFA - STATICCALL
        if opc in {0x20, 0xFA}:
            return True

        # Arithmetic opcodes
        if 0x01 <= opc <= 0x0b:
            return True

        # Logical opcodes
        if 0x10 <= opc <= 0x1d:
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
        # End of opcValid


    # For every possible opcode
    for opc in range(256):
        # We can't check SELFDESTRUCT using this technique
        if opc in {0xFF}:
           continue

        opcHex = hex(opc)[2:]
        print(fork, opcHex)
        if len(opcHex) == 1:
          opcHex = "0" + opcHex
        yulCode = Template("""
        {
           pop(call(gas(), 0x60A7, 0, 0,0, 0,0))

           // fails on opcodes with >20 inputs
           // (currently dup16, at 17 inputs, is the
           // one that goes deepest)
           //
           // Follow with 32 NOPs (0x5B) to handle PUSH, which has an immediate
           // operand
           verbatim_20i_0o(hex"${opcode}${nop32}",
              0x00, 0x00, 0x00, 0xFF, 0xFF,
              0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
              0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
              0xFF, 0xFF, 0xFF, 0xFF, 0xFF)

           // We only get here is the opcode is legit (and it doesn't terminate
           // execution like STOP and RETURN)
           let zero := 0
           let one := 1
           sstore(zero, one)
        }
        """).substitute(opcode=opcHex, nop32="5b"*32)
        pre = {
           TestAddress: Account(balance=0x0BA1A9CE0BA1A9CE),
           codeAddr: Account(
		balance=0,
		nonce=1,
		code=Yul(yulCode)
           ),
           goatAddr: Account(
                balance=0,
                nonce=1,
                code=Yul("{ return(0,0x100) }"),
           )
        }
        yield StateTest(env=env,
                        pre=pre,
                        txs=[tx],
                        post= postValid if opcValid(opc) else postInvalid)
