"""
abstract: Test [EIP-198: MODEXP Precompile](https://eips.ethereum.org/EIPS/eip-198)

    Tests the MODEXP precompile, located at address 0x0000..0005. Test cases from the EIP are
    labelled with `EIP-198-caseX` in the test id.
"""
from typing import List

import pytest

from ethereum_test_tools import (
    Account,
    Environment,
    StateTestFiller,
    TestAddress,
    Transaction,
    compute_create_address,
    to_address,
)


def create_modexp_tx_data(b: str, e: str, m: str, extra: str):
    """
    Generates input for the MODEXP precompile, with the inputs `b` (base), `e` (exponent),
    `m` (modulus) and optionally extra bytes to append at the end of the call input
    """
    return (
        "0x"
        + f"{int(len(b)/2):x}".zfill(64)
        + f"{int(len(e)/2):x}".zfill(64)
        + f"{int(len(m)/2):x}".zfill(64)
        + b
        + e
        + m
        + extra
    )


@pytest.mark.valid_from("Byzantium")
@pytest.mark.parametrize(
    ["input", "output"],
    [
        # format: ([b, e, m, extraData?], [callSuccess, returnedData])
        # Here, `b`, `e` and `m` are the inputs to the ModExp precompile
        # The output callSuccess is either 0 (fail of call (out-of-gas)) or 1 (call succeeded)
        # The output returnData is the expected output of the call
        # The optional extraData is extra padded data at the end of the calldata to the precompile
        (["", "", "02"], ["0x01", "0x01"]),
        (["", "", "0002"], ["0x01", "0x0001"]),
        (["00", "00", "02"], ["0x01", "0x01"]),
        (["", "01", "02"], ["0x01", "0x00"]),
        (["01", "01", "02"], ["0x01", "0x01"]),
        (["02", "01", "03"], ["0x01", "0x02"]),
        (["02", "02", "05"], ["0x01", "0x04"]),
        (["", "", ""], ["0x01", "0x"]),
        (["", "", "00"], ["0x01", "0x00"]),
        (["", "", "01"], ["0x01", "0x00"]),
        (["", "", "0001"], ["0x01", "0x0000"]),
        # Test cases from EIP 198 (Note: the cases where the call goes out-of-gas and the
        # final test case are not yet tested)
        pytest.param(
            [
                "03",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ],
            ["0x01", "0000000000000000000000000000000000000000000000000000000000000001"],
            id="EIP-198-case1",
        ),
        pytest.param(
            [
                "",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2e",
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
            ],
            ["0x01", "0000000000000000000000000000000000000000000000000000000000000000"],
            id="EIP-198-case2",
        ),
        pytest.param(
            [
                # Note: the only case which goes out-of-gas, and this is also raw input
                # which is thus not fed into create_modexp_tx-_data
                "0000000000000000000000000000000000000000000000000000000000000000"
                "0000000000000000000000000000000000000000000000000000000000000020"
                "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe"
                "fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffd"
            ],
            ["0x00", "0000000000000000000000000000000000000000000000000000000000000000"],
            id="EIP-198-case3",
        ),
        pytest.param(
            [
                "03",
                "ffff",
                "8000000000000000000000000000000000000000000000000000000000000000",
                "07",
            ],
            ["0x01", "0x3b01b01ac41f2d6e917c6d6a221ce793802469026d9ab7578fa2e79e4da6aaab"],
            id="EIP-198-case4",
        ),
        pytest.param(
            [
                # Note: this is raw input, so not fed into create_modexp_tx_data
                "0000000000000000000000000000000000000000000000000000000000000001"
                "0000000000000000000000000000000000000000000000000000000000000002"
                "0000000000000000000000000000000000000000000000000000000000000020"
                "03"
                "ffff"
                "80"
            ],
            ["0x01", "0x3b01b01ac41f2d6e917c6d6a221ce793802469026d9ab7578fa2e79e4da6aaab"],
            id="EIP-198-case5",
        ),
    ],
)
def test_modexp(state_test: StateTestFiller, input: List[str], output: str):
    """
    Test the MODEXP precompile
    """
    env = Environment()
    pre = {TestAddress: Account(balance=1000000000000000000000)}
    post = {}

    account = to_address(0x100)

    pre[account] = Account(
        code=(
            # Store all CALLDATA into memory (offset 0)
            """0x366000600037"""
            +
            # Setup stack to CALL into ModExp with the CALLDATA and CALL into it (+ pop value)
            """60006000366000600060055AF1"""
            +
            # Store the returned CALL status (success = 1, fail = 0) into slot 0:
            """600055"""
            +
            # Store contract deployment code to deploy the returned data from ModExp as
            # contract code (16 bytes)
            """7F601038036010600039601038036000F300000000000000000000000000000000600052"""
            +
            # RETURNDATACOPY the returned data from ModExp into memory (offset 16 bytes)
            """3D600060103E"""
            +
            # CREATE contract with the deployment code + the returned data from ModExp
            """3D60100160006000F0"""
            +
            # STOP (handy for tracing)
            "00"
        )
    )

    data = ""
    if len(input) == 1:
        data = input[0]
    else:
        if len(input) < 4:
            input.append("")
        data = create_modexp_tx_data(*input)

    tx = Transaction(
        ty=0x0,
        nonce=0,
        to=account,
        data=data,
        gas_limit=500000,
        gas_price=10,
        protected=True,
    )
    if output[0] != "0x00":
        # Note: This account is only created if the CALL output is 1. Otherwise, it is not created.
        contract_address = compute_create_address(account, tx.nonce)
        post[contract_address] = Account(code=output[1])
    post[account] = Account(storage=dict([("0x00", output[0])]))

    state_test(env=env, pre=pre, post=post, tx=tx)
