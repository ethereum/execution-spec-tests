"""
Pre-allocation fixtures using for test filling.
"""

from itertools import count
from random import randint
from typing import Iterator, List, Literal, Tuple

import pytest
from pydantic import PrivateAttr

from ethereum_test_base_types import Number, StorageRootType, ZeroPaddedHexNumber
from ethereum_test_base_types.conversions import (
    BytesConvertible,
    FixedSizeBytesConvertible,
    NumberConvertible,
)
from ethereum_test_rpc import EthRPC
from ethereum_test_rpc.types import TransactionByHashResponse
from ethereum_test_tools import EOA, Account, Address
from ethereum_test_tools import Alloc as BaseAlloc
from ethereum_test_tools import AuthorizationTuple, Initcode
from ethereum_test_tools import Opcodes as Op
from ethereum_test_tools import (
    Storage,
    Transaction,
    cost_memory_bytes,
    eip_2028_transaction_data_cost,
)
from ethereum_test_types.eof.v1 import Container
from ethereum_test_vm import Bytecode, EVMCodeType, Opcodes


def pytest_addoption(parser):
    """
    Adds command-line options to pytest.
    """
    pre_alloc_group = parser.getgroup("pre_alloc", "Arguments defining pre-allocation behavior.")
    pre_alloc_group.addoption(
        "--eoa-start",
        action="store",
        dest="eoa_iterator_start",
        default=randint(0, 2**256),
        type=int,
        help="The start private key from which tests will deploy EOAs.",
    )
    pre_alloc_group.addoption(
        "--evm-code-type",
        action="store",
        dest="evm_code_type",
        default=None,
        type=EVMCodeType,
        choices=list(EVMCodeType),
        help="Type of EVM code to deploy in each test by default.",
    )


@pytest.hookimpl(trylast=True)
def pytest_report_header(config):
    """A pytest hook called to obtain the report header."""
    bold = "\033[1m"
    reset = "\033[39;49m"
    eoa_start = config.getoption("eoa_iterator_start")
    header = [
        (bold + f"Start seed for EOA: {eoa_start} " + reset),
    ]
    return header


@pytest.fixture(scope="session")
def eoa_iterator(request) -> Iterator[EOA]:
    """
    Returns an iterator that generates EOAs.
    """
    eoa_start = request.config.getoption("eoa_iterator_start")
    print(f"Starting EOA index: {eoa_start}")
    return iter(EOA(key=i, nonce=0) for i in count(start=eoa_start))


class Alloc(BaseAlloc):
    """
    A custom class that inherits from the original Alloc class.
    """

    _sender: EOA = PrivateAttr(...)
    _eth_rpc: EthRPC = PrivateAttr(...)
    _txs: List[Transaction] = PrivateAttr(default_factory=list)
    _deployed_contracts: List[Tuple[Address, bytes]] = PrivateAttr(default_factory=list)
    _funded_eoa: List[EOA] = PrivateAttr(default_factory=list)
    _evm_code_type: EVMCodeType | None = PrivateAttr(None)
    _chain_id: int = PrivateAttr(...)

    def __init__(
        self,
        *args,
        sender: EOA,
        eth_rpc: EthRPC,
        eoa_iterator: Iterator[EOA],
        chain_id: int,
        evm_code_type: EVMCodeType | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._sender = sender
        self._eth_rpc = eth_rpc
        self._eoa_iterator = eoa_iterator
        self._evm_code_type = evm_code_type
        self._chain_id = chain_id

    def __setitem__(self, address: Address | FixedSizeBytesConvertible, account: Account | None):
        """
        Sets the account associated with an address.
        """
        raise ValueError("Tests are not allowed to set pre-alloc items in execute mode")

    def code_pre_processor(
        self, code: Bytecode | Container, *, evm_code_type: EVMCodeType | None
    ) -> Bytecode | Container:
        """
        Pre-processes the code before setting it.
        """
        if evm_code_type is None:
            evm_code_type = self._evm_code_type
        if evm_code_type == EVMCodeType.EOF_V1:
            if not isinstance(code, Container):
                if isinstance(code, Bytecode) and not code.terminating:
                    return Container.Code(code + Opcodes.STOP)
                return Container.Code(code)
        return code

    def deploy_contract(
        self,
        code: BytesConvertible,
        *,
        storage: Storage | StorageRootType = {},
        balance: NumberConvertible = 0,
        nonce: NumberConvertible = 1,
        address: Address | None = None,
        evm_code_type: EVMCodeType | None = None,
        label: str | None = None,
    ) -> Address:
        """
        Deploy a contract to the allocation.
        """
        assert address is None, "address parameter is not supported"

        if not isinstance(storage, Storage):
            storage = Storage(storage)  # type: ignore

        initcode_prefix = Bytecode()

        deploy_gas_limit = 21_000 + 32_000

        if len(storage.root) > 0:
            initcode_prefix += sum(Op.SSTORE(key, value) for key, value in storage.root.items())
            deploy_gas_limit += len(storage.root) * 22_600

        assert isinstance(code, Bytecode) or isinstance(
            code, Container
        ), f"incompatible code type: {type(code)}"
        code = self.code_pre_processor(code, evm_code_type=evm_code_type)

        deploy_gas_limit += len(bytes(code)) * 200

        initcode: Bytecode | Container

        if evm_code_type == EVMCodeType.EOF_V1:
            assert isinstance(code, Container)
            initcode = Container.Init(deploy_container=code, initcode_prefix=initcode_prefix)
        else:
            initcode = Initcode(deploy_code=code, initcode_prefix=initcode_prefix)
            deploy_gas_limit += cost_memory_bytes(len(bytes(initcode)), 0)

        deploy_gas_limit += eip_2028_transaction_data_cost(bytes(initcode))

        # Limit the gas limit
        deploy_gas_limit = min(deploy_gas_limit * 2, 30_000_000)
        print(f"Deploying contract with gas limit: {deploy_gas_limit}")

        deploy_tx = Transaction(
            sender=self._sender,
            to=None,
            data=initcode,
            value=balance,
            gas_limit=deploy_gas_limit,
        ).with_signature_and_sender()
        self._eth_rpc.send_transaction(deploy_tx)
        self._txs.append(deploy_tx)

        contract_address = deploy_tx.created_contract
        self._deployed_contracts.append((contract_address, bytes(code)))

        assert Number(nonce) >= 1, "impossible to deploy contract with nonce lower than one"

        super().__setitem__(
            contract_address,
            Account(
                nonce=nonce,
                balance=balance,
                code=code,
                storage=storage,
            ),
        )

        contract_address.label = label
        return contract_address

    def fund_eoa(
        self,
        amount: NumberConvertible | None = None,
        label: str | None = None,
        storage: Storage | None = None,
        delegation: Address | Literal["Self"] | None = None,
    ) -> EOA:
        """
        Add a previously unused EOA to the pre-alloc with the balance specified by `amount`.
        """
        if storage is not None:
            raise ValueError("EOAs storage support needs to be updated")
        eoa = next(self._eoa_iterator)
        # Send a transaction to fund the EOA
        if amount is None:
            amount = self.eoa_fund_amount_default

        if delegation is not None:
            if not isinstance(delegation, Address) and delegation == "Self":
                delegation = eoa
            fund_tx = Transaction(
                sender=self._sender,
                to=eoa,
                value=amount,
                authorization_list=[
                    AuthorizationTuple(
                        chain_id=self._chain_id,
                        address=delegation,
                        nonce=eoa.nonce,
                        signer=eoa,
                    ),
                ],
                gas_limit=100_000,
            ).with_signature_and_sender()
        else:
            fund_tx = Transaction(
                sender=self._sender,
                to=eoa,
                value=amount,
            ).with_signature_and_sender()

        self._eth_rpc.send_transaction(fund_tx)
        self._txs.append(fund_tx)
        super().__setitem__(
            eoa,
            Account(
                nonce=eoa.nonce,
                balance=amount,
            ),
        )
        self._funded_eoa.append(eoa)
        return eoa

    def fund_address(self, address: Address, amount: NumberConvertible):
        """
        Fund an address with a given amount.

        If the address is already present in the pre-alloc the amount will be
        added to its existing balance.
        """
        fund_tx = Transaction(
            sender=self._sender,
            to=address,
            value=amount,
        ).with_signature_and_sender()
        self._eth_rpc.send_transaction(fund_tx)
        self._txs.append(fund_tx)
        if address in self:
            account = self[address]
            if account is not None:
                current_balance = account.balance or 0
                account.balance = ZeroPaddedHexNumber(current_balance + Number(amount))
                return

        super().__setitem__(address, Account(balance=amount))

    def wait_for_transactions(self) -> List[TransactionByHashResponse]:
        """
        Wait for all transactions to be included in blocks.
        """
        return self._eth_rpc.wait_for_transactions(self._txs)


@pytest.fixture(autouse=True)
def evm_code_type(request: pytest.FixtureRequest) -> EVMCodeType:
    """
    Returns the default EVM code type for all tests (LEGACY).
    """
    parameter_evm_code_type = request.config.getoption("evm_code_type")
    if parameter_evm_code_type is not None:
        assert type(parameter_evm_code_type) is EVMCodeType, "Invalid EVM code type"
        return parameter_evm_code_type
    return EVMCodeType.LEGACY


@pytest.fixture(autouse=True, scope="function")
def pre(
    sender_key: EOA,
    eoa_iterator: Iterator[EOA],
    eth_rpc: EthRPC,
    evm_code_type: EVMCodeType,
    chain_id: int,
) -> Alloc:
    """
    Returns the default pre allocation for all tests (Empty alloc).
    """
    return Alloc(
        sender=sender_key,
        eth_rpc=eth_rpc,
        eoa_iterator=eoa_iterator,
        evm_code_type=evm_code_type,
        chain_id=chain_id,
    )
