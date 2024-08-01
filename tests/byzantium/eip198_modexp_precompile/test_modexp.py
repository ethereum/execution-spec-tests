"""
abstract: Test [EIP-198: MODEXP Precompile](https://eips.ethereum.org/EIPS/eip-198)
    Tests the MODEXP precompile, located at address 0x0000..0005. Test cases from the EIP are
    labelled with `EIP-198-caseX` in the test id.
"""
from dataclasses import dataclass

import pytest
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Alloc,
    Environment,
    EVMCodeType,
    StateTestFiller,
    TestParameterGroup,
    Transaction,
    call_return_code,
)
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-198.md"
REFERENCE_SPEC_VERSION = "9e393a79d9937f579acbdcb234a67869259d5a96"


@dataclass(kw_only=True, frozen=True, repr=False)
class ModExpInput(TestParameterGroup):
    """
    Helper class that defines the MODEXP precompile inputs and creates the
    call data from them.

    Attributes:
        base (str): The base value for the MODEXP precompile.
        exponent (str): The exponent value for the MODEXP precompile.
        modulus (str): The modulus value for the MODEXP precompile.
        extra_data (str): Defines extra padded data to be added at the end of the calldata
            to the precompile. Defaults to an empty string.
    """

    base: str
    exponent: str
    modulus: str
    extra_data: str = ""

    def create_modexp_tx_data(self):
        """
        Generates input for the MODEXP precompile.
        """
        return (
            ""
            + f"{int(len(self.base)/2):x}".zfill(64)
            + f"{int(len(self.exponent)/2):x}".zfill(64)
            + f"{int(len(self.modulus)/2):x}".zfill(64)
            + self.base
            + self.exponent
            + self.modulus
            + self.extra_data
        )


@dataclass(kw_only=True, frozen=True, repr=False)
class ModExpRawInput(TestParameterGroup):
    """
    Helper class to directly define a raw input to the MODEXP precompile.
    """

    raw_input: str

    def create_modexp_tx_data(self):
        """
        The raw input is already the MODEXP precompile input.
        """
        return self.raw_input


@dataclass(kw_only=True, frozen=True, repr=False)
class ExpectedOutput(TestParameterGroup):
    """
    Expected test result.

    Attributes:
        call_return_success (str): The return_code from CALL.
        returned_data (bytes): The output returnData is the expected output of the call
    """

    call_return_success: bool
    returned_data: bytes


@pytest.mark.valid_from("Byzantium")
@pytest.mark.parametrize(
    ["input", "output"],
    [
        (
            ModExpInput(base="", exponent="", modulus="02"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("01")),
        ),
        (
            ModExpInput(base="", exponent="", modulus="0002"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("0001")),
        ),
        (
            ModExpInput(base="00", exponent="00", modulus="02"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("01")),
        ),
        (
            ModExpInput(base="", exponent="01", modulus="02"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("00")),
        ),
        (
            ModExpInput(base="01", exponent="01", modulus="02"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("01")),
        ),
        (
            ModExpInput(base="02", exponent="01", modulus="03"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("02")),
        ),
        (
            ModExpInput(base="02", exponent="02", modulus="05"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("04")),
        ),
        (
            ModExpInput(base="", exponent="", modulus=""),
            ExpectedOutput(call_return_success=True, returned_data=b""),
        ),
        (
            ModExpInput(base="", exponent="", modulus="00"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("00")),
        ),
        (
            ModExpInput(base="", exponent="", modulus="01"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("00")),
        ),
        (
            ModExpInput(base="", exponent="", modulus="0001"),
            ExpectedOutput(call_return_success=True, returned_data=bytes.fromhex("0000")),
        ),
        # Test cases from EIP 198.
        pytest.param(
            ModExpInput(
                base="03",
                exponent="fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                modulus="fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ),
            ExpectedOutput(
                call_return_success=True,
                returned_data=bytes.fromhex(
                    "0000000000000000000000000000000000000000000000000000000000000001"
                ),
            ),
            id="EIP-198-case1",
        ),
        pytest.param(
            ModExpInput(
                base="",
                exponent="fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                modulus="fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ),
            ExpectedOutput(
                call_return_success=True,
                returned_data=bytes.fromhex(
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            ),
            id="EIP-198-case2",
        ),
        pytest.param(  # Note: This is the only test case which goes out-of-gas.
            ModExpRawInput(
                raw_input="0000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000020"
                "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffd"
            ),
            ExpectedOutput(
                call_return_success=False,
                returned_data=bytes.fromhex(
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
            ),
            id="EIP-198-case3-raw-input-out-of-gas",
        ),
        pytest.param(
            ModExpInput(
                base="03",
                exponent="ffff",
                modulus="8000000000000000000000000000000000000000000000000000000000000000",
                extra_data="07",
            ),
            ExpectedOutput(
                call_return_success=True,
                returned_data=bytes.fromhex(
                    "3b01b01ac41f2d6e917c6d6a221ce793802469026d9ab7578fa2e79e4da6aaab"
                ),
            ),
            id="EIP-198-case4-extra-data_07",
        ),
        pytest.param(
            ModExpRawInput(
                raw_input="0000000000000000000000000000000000000000000000000000000000000001"
                "0000000000000000000000000000000000000000000000000000000000000002"
                "0000000000000000000000000000000000000000000000000000000000000020"
                "03"
                "ffff"
                "80"
            ),
            ExpectedOutput(
                call_return_success=True,
                returned_data=bytes.fromhex(
                    "3b01b01ac41f2d6e917c6d6a221ce793802469026d9ab7578fa2e79e4da6aaab"
                ),
            ),
            id="EIP-198-case5-raw-input",
        ),
    ],
    ids=lambda param: param.__repr__(),  # only required to remove parameter names (input/output)
)
@pytest.mark.with_all_evm_code_types
def test_modexp(
    state_test: StateTestFiller,
    input: ModExpInput,
    output: ExpectedOutput,
    pre: Alloc,
    evm_code_type: EVMCodeType,
):
    """
    Test the MODEXP precompile
    """
    env = Environment()
    sender = pre.fund_eoa()
    call_opcode = Op.CALL if evm_code_type == EVMCodeType.LEGACY else Op.EXTCALL
    account_code = (
        # Store all CALLDATA into memory (offset 0)
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE())
        # Store the returned CALL status (success = 1, fail = 0) into slot 0:
        + Op.SSTORE(
            0,
            # Setup stack to CALL into ModExp with the CALLDATA and CALL into it (+ pop value)
            call_opcode(address=0x05, args_size=Op.CALLDATASIZE()),
        )
        # RETURNDATACOPY the returned data from ModExp into memory
        + Op.RETURNDATACOPY(0, 0, Op.RETURNDATASIZE())
        + Op.SSTORE(1, Op.SHA3(0, Op.RETURNDATASIZE()))
        + Op.STOP()
    )
    account = pre.deploy_contract(account_code)

    tx = Transaction(
        to=account,
        data=input.create_modexp_tx_data(),
        gas_limit=500_000,
        protected=True,
        sender=sender,
    )

    post = {}
    if output.call_return_success:
        post[account] = Account(
            storage={
                0: call_return_code(call_opcode, True),
                1: keccak256(output.returned_data),
            }
        )
    else:
        post[account] = Account(
            storage={
                0: 0,
                1: 0,
            }
        )

    state_test(env=env, pre=pre, post=post, tx=tx)
