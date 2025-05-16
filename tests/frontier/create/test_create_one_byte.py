"""
The test calls CREATE in a loop deploying 1-byte contracts with all possible byte values,
records in storage the values that failed to deploy.
"""

import pytest

from ethereum_test_forks import Byzantium, Fork, London
from ethereum_test_tools import Account, Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools import Opcodes as Op
from ethereum_test_types import compute_create2_address, compute_create_address


@pytest.mark.valid_from("Frontier")
@pytest.mark.with_all_create_opcodes
@pytest.mark.parametrize(
    "byte",
    [f"{b:02x}" for b in range(256)],
)
def test_create_one_byte(
    state_test: StateTestFiller,
    fork: Fork,
    pre: Alloc,
    byte: str,
    create_opcode: Op,
):
    """Run create deploys with single bytes for each byte."""
    initcode = Op.MSTORE8(0, byte) + Op.RETURN(0, 1)
    sender = pre.fund_eoa()
    code = pre.deploy_contract(
        nonce=1,
        code=Op.MSTORE(0, Op.PUSH32(bytes(initcode)))
        + Op.SSTORE(byte, create_opcode(offset=32 - len(initcode), salt=0, size=len(initcode)))
        + Op.SSTORE(256, 1),
    )

    create_address = (
        compute_create_address(address=code, nonce=1)
        if create_opcode == Op.CREATE
        else compute_create2_address(address=code, salt=0, initcode=initcode)
    )

    tx = Transaction(
        gas_limit=100_000,
        to=code,
        data=b"",
        nonce=0,
        sender=sender,
        protected=fork >= Byzantium,
    )
    ef_exception = byte == "ef" and fork >= London
    post = {
        code: Account(
            storage={
                256: 0 if ef_exception else 1,
                int(byte, 16): 0 if ef_exception else create_address,
            },
        ),
    }
    if not ef_exception:
        post[create_address] = Account(code=byte)
    state_test(env=Environment(), pre=pre, post=post, tx=tx)
