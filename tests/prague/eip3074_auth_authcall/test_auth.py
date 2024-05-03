"""
Tests for EIP-3074's `AUTH` Instruction
"""

from typing import Tuple

import pytest
from coincurve.keys import PrivateKey, PublicKey
from ethereum.base_types import U256
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Address,
    Environment,
    StateTestFiller,
    TestAddress,
    TestAddress2,
    TestPrivateKey,
    TestPrivateKey2,
    Transaction,
)
from ethereum_test_tools.common.base_types import Hash
from ethereum_test_tools.vm.opcode import Opcodes as Op

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-3074.md"
REFERENCE_SPEC_VERSION = "3b5fcad6b35782f8aaeba7d4ac26004e8fbd720f"

MAGIC = b"\x04"


@pytest.mark.valid_from("Prague")
def test_all_zeros(state_test: StateTestFiller) -> None:
    """
    Test `AUTH` opcode with all zero arguments.
    """
    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=Op.SSTORE(1, Op.ISZERO(Op.AUTH(0, 0, 0)))),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=50000,
    )
    post = {
        to: Account(storage={"0x01": "0x01"}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_stack_underflow(state_test: StateTestFiller) -> None:
    """
    Test `AUTH` opcode with too few stack items.
    """
    env = Environment()
    to = Address(0x100)
    invoker = Address(0x101)
    pre = {
        to: Account(code=Op.SSTORE(1, Op.ISZERO(Op.CALL(50000, invoker, 0, 0, 0, 0, 0)))),
        invoker: Account(code=Op.SSTORE(3, 1) + Op.AUTH + Op.SSTORE(2, 1)),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=100000,
    )
    post = {
        to: Account(storage={"0x01": "0x01"}),
        invoker: Account(storage={"0x02": "0x00", "0x03": "0x00"}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_expand_memory(state_test: StateTestFiller) -> None:
    """
    Test an `AUTH` that expands memory.
    """
    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=Op.SSTORE(1, Op.ISZERO(Op.AUTH(0, 24000, 1)))),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=60000,
    )
    post = {
        to: Account(storage={"0x01": "0x01"}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


def sign_authorization(
    private_key: str, magic: bytes, chain_id: int, nonce: int, invoker: Address, commit: Hash
) -> Tuple[Address, bytes]:
    """
    Sign an authorization and return the authority and calldata in the format
    expected for `auth`.
    """
    signing_bytes = (
        magic
        + U256(chain_id).to_be_bytes32()
        + U256(nonce).to_be_bytes32()
        + invoker.rjust(32, b"\x00")
        + commit
    )

    signing_hash = keccak256(signing_bytes)
    signature_bytes = PrivateKey(secret=Hash(private_key)).sign_recoverable(
        signing_hash, hasher=None
    )
    public_key = PublicKey.from_signature_and_message(signature_bytes, signing_hash, hasher=None)

    authority = keccak256(public_key.format(compressed=False)[1:])[32 - 20 :]

    r = signature_bytes[:32]
    s = signature_bytes[32:64]
    y_parity = signature_bytes[64:65]

    return (Address(authority), y_parity + r + s + commit)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("chain_id,chain_id_ok", [(1, True), (5, False)])
@pytest.mark.parametrize("nonce,nonce_ok", [(0, False), (1, True), (2, False)])
@pytest.mark.parametrize("invoker,invoker_ok", [(Address(0x101), False), (Address(0x100), True)])
@pytest.mark.parametrize("magic,magic_ok", [(b"\x03", False), (MAGIC, True)])
@pytest.mark.parametrize("authority,authority_ok", [(TestAddress, True), (TestAddress2, False)])
def test_self(
    state_test: StateTestFiller,
    chain_id: int,
    nonce: int,
    invoker: Address,
    magic: bytes,
    authority: Address,
    chain_id_ok: bool,
    nonce_ok: bool,
    invoker_ok: bool,
    magic_ok: bool,
    authority_ok: bool,
) -> None:
    """
    Test `auth` when `authority == tx.origin`.
    """
    commit = Hash("0x01")

    signer, calldata = sign_authorization(
        TestPrivateKey,
        magic,
        chain_id,
        nonce,
        invoker,
        commit,
    )
    assert signer == TestAddress

    code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.AUTH(Op.PUSH20(authority), 0, Op.CALLDATASIZE)
    )

    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=1000000,
        data=calldata,
    )

    results = (chain_id_ok, nonce_ok, invoker_ok, magic_ok, authority_ok)
    expected = "0x01" if all(results) else "0x00"
    post = {
        to: Account(storage={"0x01": expected}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("nonce,nonce_ok", [(0, True), (1, False)])
def test_sponsor(
    state_test: StateTestFiller,
    nonce: int,
    nonce_ok: bool,
) -> None:
    """
    Test `auth` when `authority != tx.origin`.
    """
    commit = Hash("0x00")
    invoker = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey2,
        MAGIC,
        1,
        nonce,
        invoker,
        commit,
    )
    assert authority == TestAddress2

    code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.AUTH(Op.PUSH20(authority), 0, Op.CALLDATASIZE)
    )

    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=1000000,
        data=calldata,
    )

    results = (nonce_ok,)
    expected = "0x01" if all(results) else "0x00"
    post = {
        to: Account(storage={"0x01": expected}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize(
    "commit,ok",
    [
        # Commit to 0xFF..., put 0xFF... in memory, fail because auth sees 0x00...
        (Hash(b"\xFF" * 32), False),
        # Commit to 0x00..., but put 0xFF... in memory, pass because auth sees 0x00...
        (Hash("0x00"), True),
    ],
)
def test_short_memory(
    state_test: StateTestFiller,
    commit: Hash,
    ok: bool,
) -> None:
    """
    Test `auth` with less bytes than expected.
    """
    invoker = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey,
        MAGIC,
        1,
        1,
        invoker,
        commit,
    )
    assert authority == TestAddress

    # Strip off the commit and replace it with non-zero bytes.
    calldata = calldata[: -len(commit)] + (b"\xff" * len(commit))

    code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.AUTH(Op.PUSH20(authority), 0, Op.SUB(Op.CALLDATASIZE, len(commit)))
    )

    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=1000000,
        data=calldata,
    )

    expected = "0x01" if ok else "0x00"
    post = {
        to: Account(storage={"0x01": expected}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_long_memory(
    state_test: StateTestFiller,
) -> None:
    """
    Test `auth` with more bytes than expected.
    """
    commit = Hash("0x01")
    invoker = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey,
        MAGIC,
        1,
        1,
        invoker,
        commit,
    )
    assert authority == TestAddress

    calldata += b"\xAA" * 1500

    dest = 107  # Non-zero non-multiple of 32, just to be weird.
    code = Op.CALLDATACOPY(dest, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.AUTH(Op.PUSH20(authority), dest, Op.CALLDATASIZE)
    )

    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=1000000,
        data=calldata,
    )

    post = {
        to: Account(storage={"0x01": "0x01"}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
def test_extcodesize(
    state_test: StateTestFiller,
) -> None:
    """
    Test `auth` when authority has code.
    """
    commit = Hash("0x01")
    invoker = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey2,
        MAGIC,
        1,
        0,
        invoker,
        commit,
    )
    assert authority == TestAddress2

    # Put the gas cost of an extcodesize into storage to prove authority has been warmed.
    code = (
        Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
        + Op.SSTORE(1, Op.ISZERO(Op.AUTH(Op.PUSH20(authority), 0, Op.CALLDATASIZE)))
        + Op.SSTORE(2, Op.SUB(0, Op.SUB(Op.POP(Op.EXTCODESIZE(authority)) + Op.GAS, Op.GAS)))
    )

    env = Environment()
    to = Address(0x100)
    pre = {
        to: Account(code=code),
        TestAddress: Account(balance=1000000000000000000000),
        TestAddress2: Account(code=Op.INVALID),
    }
    tx = Transaction(
        to=to,
        gas_limit=1000000,
        data=calldata,
    )

    post = {
        to: Account(storage={"0x01": "0x01", "0x02": 100 + 2 + 2 + 3}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("invoker,ok", [(Address("0x100"), True), (Address("0x101"), False)])
def test_delegatecall_other(
    state_test: StateTestFiller,
    invoker: Address,
    ok: bool,
) -> None:
    """
    Test `auth` when the invoker `delegatecall`s into a different contract.
    """
    commit = Hash("0x01")
    to = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey2,
        MAGIC,
        1,
        0,
        invoker,
        commit,
    )
    assert authority == TestAddress2

    target = Address("0x101")
    target_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        2, Op.ISZERO(Op.AUTH(Op.PUSH20(authority), 0, Op.CALLDATASIZE))
    )

    invoker_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.DELEGATECALL(100000, target, 0, Op.CALLDATASIZE, 0, 0)
    )

    env = Environment()
    pre = {
        target: Account(code=target_code),
        to: Account(code=invoker_code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=10000000,
        data=calldata,
    )

    expected = "0x00" if ok else "0x01"
    post = {
        to: Account(storage={"0x01": "0x01", "0x02": expected}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


@pytest.mark.valid_from("Prague")
@pytest.mark.parametrize("invoker,ok", [(Address("0x100"), True), (Address("0x101"), False)])
def test_callcode_other(
    state_test: StateTestFiller,
    invoker: Address,
    ok: bool,
) -> None:
    """
    Test `auth` when the invoker `callcode`s into a different contract.
    """
    commit = Hash("0x01")
    to = Address("0x100")

    authority, calldata = sign_authorization(
        TestPrivateKey2,
        MAGIC,
        1,
        0,
        invoker,
        commit,
    )
    assert authority == TestAddress2

    target = Address("0x101")
    target_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        2, Op.ISZERO(Op.AUTH(Op.PUSH20(authority), 0, Op.CALLDATASIZE))
    )

    invoker_code = Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
        1, Op.CALLCODE(100000, target, 0, 0, Op.CALLDATASIZE, 0, 0)
    )

    env = Environment()
    pre = {
        target: Account(code=target_code),
        to: Account(code=invoker_code),
        TestAddress: Account(balance=1000000000000000000000),
    }
    tx = Transaction(
        to=to,
        gas_limit=10000000,
        data=calldata,
    )

    expected = "0x00" if ok else "0x01"
    post = {
        to: Account(storage={"0x01": "0x01", "0x02": expected}),
    }

    state_test(env=env, pre=pre, post=post, tx=tx)


# TODO: Test warm vs. cold access cost
# TODO: Clear authority after setting
# TODO: auth+authcall inside staticcall without value
# TODO: auth+authcall inside staticcall with value
# TODO: auth -> delegatecall -> authcall fails
