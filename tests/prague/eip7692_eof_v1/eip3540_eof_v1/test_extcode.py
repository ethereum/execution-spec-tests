"""
test execution semantics changes
"""
from typing import Dict

import pytest
from ethereum.crypto.hash import keccak256

from ethereum_test_tools import (
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    StateTestFiller,
    Storage,
    Transaction,
)
from ethereum_test_tools.eof.v1 import Container, Section
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .. import EOF_FORK_NAME

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "90f716078d0b08ce508a1e57803f885cc2f2e15e"


def test_legacy_calls_eof_sstore(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """Test EXTCODE* opcodes calling EOF and legacy contracts"""
    env = Environment()
    address_eof_contract = pre.deploy_contract(
        Container(
            sections=[
                Section.Code(
                    code=Op.RJUMP[0] + Op.STOP,
                )
            ]
        )
    )
    legacy_code = Op.PUSH1(2) + Op.JUMPDEST + Op.STOP
    address_legacy_contract = pre.deploy_contract(legacy_code)

    storage_test = Storage()
    test_contract_code = (
        Op.SSTORE(storage_test.store_next(4), Op.EXTCODESIZE(address_legacy_contract))
        + Op.EXTCODECOPY(address_legacy_contract, 0, 0, Op.EXTCODESIZE(address_legacy_contract))
        + Op.SSTORE(
            storage_test.store_next(bytes(legacy_code) + (b"\0" * (32 - len(legacy_code)))),
            Op.MLOAD(0),
        )
        + Op.SSTORE(
            storage_test.store_next(legacy_code.keccak256()),
            Op.EXTCODEHASH(address_legacy_contract),
        )
        + Op.SSTORE(storage_test.store_next(2), Op.EXTCODESIZE(address_eof_contract))
        + Op.EXTCODECOPY(address_eof_contract, 0x20, 0, Op.EXTCODESIZE(address_eof_contract))
        + Op.SSTORE(storage_test.store_next(b"\xef" + (b"\0" * 31)), Op.MLOAD(0x20))
        + Op.SSTORE(
            storage_test.store_next(keccak256(b"\xef\x00")),
            Op.EXTCODEHASH(address_eof_contract),
        )
    )
    address_test_contract = pre.deploy_contract(test_contract_code)

    sender = pre.fund_eoa()

    tx = Transaction(
        sender=sender,
        to=address_test_contract,
        gas_limit=50_000_000,
        gas_price=10,
        protected=False,
        data="",
    )

    post = {
        address_test_contract: Account(storage=storage_test),
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@pytest.mark.pre_alloc_modifier
def test_legacy_calls_mainnet_contracts(
    state_test: StateTestFiller,
    pre: Alloc,
):
    """
    Test existing mainnet contracts that start with 0xef do not exhibit the same
    behavior as the EOF contracts when using EXTCODE* opcodes.
    """
    env = Environment()
    storage_test = Storage()

    mainnet_contracts: Dict[Address, bytes] = {
        Address(0xCA7BF67AB492B49806E24B6E2E4EC105183CAA01): b"\xef",
        Address(0x897DA0F23CCC5E939EC7A53032C5E80FD1A947EC): b"\xef",
        Address(
            0x6E51D4D9BE52B623A3D3A2FA8D3C5E3E01175CD0
        ): b"\xef\xf0\x9f\x91\x8b\xf0\x9f\x9f\xa9",
    }

    test_contract_code = Bytecode()
    for address, code in mainnet_contracts.items():
        test_contract_code += (
            Op.SSTORE(storage_test.store_next(len(code)), Op.EXTCODESIZE(address))
            + Op.EXTCODECOPY(address, 0, 0, Op.EXTCODESIZE(address))
            + Op.SSTORE(storage_test.store_next(code.ljust(32, b"\0")), Op.MLOAD(0))
            + Op.SSTORE(storage_test.store_next(keccak256(code)), Op.EXTCODEHASH(address))
        )

    address_test_contract = pre.deploy_contract(
        test_contract_code,
        storage=storage_test.canary_storage(),
    )

    for address, code in mainnet_contracts.items():
        pre[address] = Account(code=code)

    sender = pre.fund_eoa()

    tx = Transaction(
        sender=sender,
        to=address_test_contract,
        gas_limit=50000000,
    )

    post = {
        address_test_contract: Account(storage=storage_test),
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )
