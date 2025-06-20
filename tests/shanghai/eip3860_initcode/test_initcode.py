"""
abstract: Test [EIP-3860: Limit and meter initcode](https://eips.ethereum.org/EIPS/eip-3860)
    Tests for  [EIP-3860: Limit and meter initcode](https://eips.ethereum.org/EIPS/eip-3860).

note: Tests ported from:
    - [ethereum/tests/pull/990](https://github.com/ethereum/tests/pull/990)
    - [ethereum/tests/pull/1012](https://github.com/ethereum/tests/pull/990)
"""

from typing import Iterator, List

import pytest

from ethereum_test_forks import Fork
from ethereum_test_tools import (
    EOA,
    AccessList,
    Account,
    Address,
    Alloc,
    Bytecode,
    Environment,
    Initcode,
    StateTestFiller,
    Transaction,
    TransactionException,
    TransactionReceipt,
    ceiling_division,
    compute_create_address,
)
from ethereum_test_tools.utility.pytest import ParameterSet
from ethereum_test_tools.vm.opcode import Opcodes as Op

from .helpers import INITCODE_RESULTING_DEPLOYED_CODE, get_create_id
from .spec import ref_spec_3860

REFERENCE_SPEC_GIT_PATH = ref_spec_3860.git_path
REFERENCE_SPEC_VERSION = ref_spec_3860.version

pytestmark = pytest.mark.valid_from("Shanghai")


"""
Initcode templates used throughout the tests
"""


def initcode_ones_max_limit(fork: Fork) -> Initcode:
    """Initcode with all ones."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size(),
        padding_byte=0x01,
        name="max_size_ones",
    )


def initcode_zeros_max_limit(fork: Fork) -> Initcode:
    """Initcode with all zeros."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size(),
        padding_byte=0x00,
        name="max_size_zeros",
    )


def initcode_ones_over_limit(fork: Fork) -> Initcode:
    """Initcode with all ones over the max limit."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size() + 1,
        padding_byte=0x01,
        name="over_limit_ones",
    )


def initcode_zeros_over_limit(fork: Fork) -> Initcode:
    """Initcode with all zeros over the max limit."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size() + 1,
        padding_byte=0x00,
        name="over_limit_zeros",
    )


def initcode_32_bytes(fork: Fork) -> Initcode:
    """Initcode with 32 bytes."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=32,
        padding_byte=0x00,
        name="32_bytes",
    )


def initcode_33_bytes(fork: Fork) -> Initcode:
    """Initcode with 33 bytes."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=33,
        padding_byte=0x00,
        name="33_bytes",
    )


def initcode_max_minus_32_bytes(fork: Fork) -> Initcode:
    """Initcode with max - 32 bytes."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size() - 32,
        padding_byte=0x00,
        name="max_minus_32_bytes",
    )


def initcode_max_minus_32_plus_1_bytes(fork: Fork) -> Initcode:
    """Initcode with max - 32 + 1 bytes."""
    return Initcode(
        deploy_code=INITCODE_RESULTING_DEPLOYED_CODE,
        initcode_length=fork.max_initcode_size() - 32 + 1,
        padding_byte=0x00,
        name="max_minus_32_plus_1_bytes",
    )


def initcode_empty(fork: Fork) -> Initcode:
    """Initcode with 0 bytes."""
    empty_initcode = Initcode(
        name="empty",
    )
    empty_initcode._bytes_ = bytes()
    empty_initcode.deployment_gas = 0
    empty_initcode.execution_gas = 0
    return empty_initcode


def initcode_single_byte(fork: Fork) -> Initcode:
    """Initcode with 1 byte."""
    single_byte_initcode = Initcode(
        name="single_byte",
    )
    single_byte_initcode._bytes_ = bytes(Op.STOP)
    single_byte_initcode.deployment_gas = 0
    single_byte_initcode.execution_gas = 0
    return single_byte_initcode


"""
Test cases using a contract creating transaction
"""


def contract_creating_tx_cases(
    fork: Fork,
) -> Iterator[ParameterSet]:
    """Generate test cases for contract creating transactions."""

    def param(initcode: Initcode, exception: TransactionException | None = None) -> ParameterSet:
        return pytest.param(
            initcode,
            exception,
            marks=[pytest.mark.exception_test] if exception else [],
            id=initcode._name_,
        )

    yield param(initcode_ones_max_limit(fork))
    yield param(initcode_zeros_max_limit(fork))
    yield param(initcode_zeros_over_limit(fork), TransactionException.INITCODE_SIZE_EXCEEDED)
    yield param(initcode_ones_over_limit(fork), TransactionException.INITCODE_SIZE_EXCEEDED)


@pytest.mark.parametrize_by_fork(
    "initcode,exception",
    contract_creating_tx_cases,
)
def test_contract_creating_tx(
    state_test: StateTestFiller,
    env: Environment,
    pre: Alloc,
    post: Alloc,
    sender: EOA,
    initcode: Initcode,
    exception: TransactionException | None,
    fork: Fork,
):
    """
    Tests creating a contract using a transaction with an initcode that is
    on/over the max allowed limit.
    """
    create_contract_address = compute_create_address(
        address=sender,
        nonce=0,
    )

    tx = Transaction(
        nonce=0,
        to=None,
        data=initcode,
        gas_limit=25_000_000,
        sender=sender,
        error=exception,
    )

    if len(initcode) > fork.max_initcode_size():
        # Initcode is above the max size, tx inclusion in the block makes
        # it invalid.
        post[create_contract_address] = Account.NONEXISTENT
    else:
        # Initcode is at or below the max size, tx inclusion in the block
        # is ok and the contract is successfully created.
        post[create_contract_address] = Account(code=Op.STOP)

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


def valid_gas_test_case(initcode: Initcode, gas_test_case: str) -> bool:
    """Filter out invalid gas test case/initcode combinations."""
    if gas_test_case == "too_little_execution_gas":
        return (initcode.deployment_gas + initcode.execution_gas) > 0
    return True


def gas_test_cases(fork: Fork) -> Iterator[ParameterSet]:
    """Generate test cases for gas usage."""
    for i in [
        initcode_zeros_max_limit(fork),
        initcode_ones_max_limit(fork),
        initcode_empty(fork),
        initcode_single_byte(fork),
        initcode_32_bytes(fork),
        initcode_33_bytes(fork),
        initcode_max_minus_32_bytes(fork),
        initcode_max_minus_32_plus_1_bytes(fork),
    ]:
        for g in [
            "too_little_intrinsic_gas",
            "exact_intrinsic_gas",
            "too_little_execution_gas",
            "exact_execution_gas",
        ]:
            if valid_gas_test_case(i, g):
                if g == "too_little_intrinsic_gas":
                    marks = [pytest.mark.exception_test]
                else:
                    marks = []
                yield pytest.param(i, g, marks=marks, id=f"{i._name_}-{g}")


@pytest.mark.parametrize_by_fork(
    "initcode,gas_test_case",
    gas_test_cases,
)
class TestContractCreationGasUsage:
    """
    Tests the following cases that verify the gas cost behavior of a
    contract creating transaction.

    1. Test with exact intrinsic gas minus one, contract create fails
        and tx is invalid.
    2. Test with exact intrinsic gas, contract create fails,
        but tx is valid.
    3. Test with exact execution gas minus one, contract create fails,
        but tx is valid.
    4. Test with exact execution gas, contract create succeeds.

    Initcode must be within a valid EIP-3860 length.
    """

    @pytest.fixture
    def tx_access_list(self, fork: Fork, initcode: Initcode) -> List[AccessList]:
        """
        On EIP-7623, we need to use an access list to raise the intrinsic gas cost to
        be above the floor data cost.
        """
        gas_costs = fork.gas_costs()
        tx_intrinsic_gas_cost_calculator = fork.transaction_intrinsic_cost_calculator()
        data_floor = tx_intrinsic_gas_cost_calculator(calldata=initcode)
        intrinsic_gas_cost = tx_intrinsic_gas_cost_calculator(
            calldata=initcode,
            contract_creation=True,
            return_cost_deducted_prior_execution=True,
        )
        if intrinsic_gas_cost > data_floor:
            return []
        access_list_count = (
            (data_floor - intrinsic_gas_cost) // gas_costs.G_ACCESS_LIST_ADDRESS
        ) + 1
        return [
            AccessList(address=Address(i + 1), storage_keys=[]) for i in range(access_list_count)
        ]

    @pytest.fixture
    def exact_intrinsic_gas(
        self, fork: Fork, initcode: Initcode, tx_access_list: List[AccessList]
    ) -> int:
        """Calculate the intrinsic tx gas cost."""
        tx_intrinsic_gas_cost_calculator = fork.transaction_intrinsic_cost_calculator()
        assert tx_intrinsic_gas_cost_calculator(
            calldata=initcode,
            contract_creation=True,
            access_list=tx_access_list,
        ) == tx_intrinsic_gas_cost_calculator(
            calldata=initcode,
            contract_creation=True,
            access_list=tx_access_list,
            return_cost_deducted_prior_execution=True,
        )
        return tx_intrinsic_gas_cost_calculator(
            calldata=initcode,
            contract_creation=True,
            access_list=tx_access_list,
        )

    @pytest.fixture
    def exact_execution_gas(self, exact_intrinsic_gas: int, initcode: Initcode) -> int:
        """Calculate total execution gas cost."""
        return exact_intrinsic_gas + initcode.deployment_gas + initcode.execution_gas

    @pytest.fixture
    def tx_error(self, gas_test_case: str) -> TransactionException | None:
        """
        Check that the transaction is invalid if too little intrinsic gas is
        specified, otherwise the tx is valid and succeeds.
        """
        if gas_test_case == "too_little_intrinsic_gas":
            return TransactionException.INTRINSIC_GAS_TOO_LOW
        return None

    @pytest.fixture
    def tx(
        self,
        sender: EOA,
        initcode: Initcode,
        gas_test_case: str,
        tx_access_list: List[AccessList],
        tx_error: TransactionException | None,
        exact_intrinsic_gas: int,
        exact_execution_gas: int,
    ) -> Transaction:
        """
        Implement the gas_test_case by setting the gas_limit of the tx
        appropriately and test whether the tx succeeds or fails with
        appropriate error.
        """
        if gas_test_case == "too_little_intrinsic_gas":
            gas_limit = exact_intrinsic_gas - 1
        elif gas_test_case == "exact_intrinsic_gas":
            gas_limit = exact_intrinsic_gas
        elif gas_test_case == "too_little_execution_gas":
            gas_limit = exact_execution_gas - 1
        elif gas_test_case == "exact_execution_gas":
            gas_limit = exact_execution_gas
        else:
            pytest.fail("Invalid gas test case provided.")

        return Transaction(
            nonce=0,
            to=None,
            access_list=tx_access_list,
            data=initcode,
            gas_limit=gas_limit,
            gas_price=10,
            error=tx_error,
            sender=sender,
            # The entire gas limit is expected to be consumed.
            expected_receipt=TransactionReceipt(gas_used=gas_limit),
        )

    @pytest.fixture
    def post(
        self,
        sender: EOA,
        initcode: Initcode,
        gas_test_case: str,
        exact_intrinsic_gas: int,
        exact_execution_gas: int,
    ) -> Alloc:
        """
        Test that contract creation fails unless enough execution gas is
        provided.
        """
        create_contract_address = compute_create_address(
            address=sender,
            nonce=0,
        )
        if gas_test_case == "exact_intrinsic_gas" and exact_intrinsic_gas == exact_execution_gas:
            # Special scenario where the execution of the initcode and
            # gas cost to deploy are zero
            return Alloc({create_contract_address: Account(code=initcode.deploy_code)})
        elif gas_test_case == "exact_execution_gas":
            return Alloc({create_contract_address: Account(code=initcode.deploy_code)})
        return Alloc({create_contract_address: Account.NONEXISTENT})

    def test_gas_usage(
        self,
        state_test: StateTestFiller,
        env: Environment,
        pre: Alloc,
        post: Alloc,
        tx: Transaction,
    ):
        """Test transaction and contract creation behavior for different gas limits."""
        state_test(
            env=env,
            pre=pre,
            post=post,
            tx=tx,
        )


def create_initcode_cases(
    fork: Fork,
) -> Iterator[ParameterSet]:
    """Generate test cases for contract creating transactions."""

    def param(initcode: Initcode) -> ParameterSet:
        return pytest.param(initcode, id=initcode._name_)

    yield param(initcode_zeros_max_limit(fork))
    yield param(initcode_ones_max_limit(fork))
    yield param(initcode_zeros_over_limit(fork))
    yield param(initcode_ones_over_limit(fork))
    yield param(initcode_empty(fork))
    yield param(initcode_single_byte(fork))
    yield param(initcode_32_bytes(fork))
    yield param(initcode_33_bytes(fork))
    yield param(initcode_max_minus_32_bytes(fork))
    yield param(initcode_max_minus_32_plus_1_bytes(fork))


@pytest.mark.parametrize_by_fork(
    "initcode",
    create_initcode_cases,
)
@pytest.mark.parametrize("opcode", [Op.CREATE, Op.CREATE2], ids=get_create_id)
class TestCreateInitcode:
    """
    Test contract creation via the CREATE/CREATE2 opcodes that have an initcode
    that is on/over the max allowed limit.
    """

    @pytest.fixture
    def create2_salt(self) -> int:
        """Salt value used for CREATE2 contract creation."""
        return 0xDEADBEEF

    @pytest.fixture
    def creator_code(self, opcode: Op, create2_salt: int) -> Bytecode:
        """Generate code for the creator contract which performs the CREATE/CREATE2 operation."""
        return (
            Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE)
            + Op.GAS
            + opcode(size=Op.CALLDATASIZE, salt=create2_salt)
            + Op.GAS
            # stack: [Gas 2, Call Result, Gas 1]
            + Op.SWAP1
            # stack: [Call Result, Gas 2, Gas 1]
            + Op.SSTORE(0, unchecked=True)
            # stack: [Gas 2, Gas 1]
            + Op.SWAP1
            # stack: [Gas 1, Gas 2]
            + Op.SUB
            # stack: [Gas 1 - Gas 2]
            + Op.SSTORE(1, unchecked=True)
        )

    @pytest.fixture
    def creator_contract_address(self, pre: Alloc, creator_code: Bytecode) -> Address:
        """Return address of creator contract."""
        return pre.deploy_contract(creator_code)

    @pytest.fixture
    def created_contract_address(  # noqa: D103
        self,
        opcode: Op,
        create2_salt: int,
        initcode: Initcode,
        creator_contract_address: Address,
    ) -> Address:
        """Calculate address of the contract created by the creator contract."""
        return compute_create_address(
            address=creator_contract_address,
            nonce=1,
            salt=create2_salt,
            initcode=initcode,
            opcode=opcode,
        )

    @pytest.fixture
    def caller_code(self, creator_contract_address: Address) -> Bytecode:
        """Generate code for the caller contract that calls the creator contract."""
        return Op.CALLDATACOPY(0, 0, Op.CALLDATASIZE) + Op.SSTORE(
            Op.CALL(5000000, creator_contract_address, 0, 0, Op.CALLDATASIZE, 0, 0), 1
        )

    @pytest.fixture
    def caller_contract_address(self, pre: Alloc, caller_code: Bytecode) -> Address:
        """Return address of the caller contract."""
        return pre.deploy_contract(caller_code)

    @pytest.fixture
    def tx(self, caller_contract_address: Address, initcode: Initcode, sender: EOA) -> Transaction:
        """Generate transaction that executes the caller contract."""
        return Transaction(
            nonce=0,
            to=caller_contract_address,
            data=initcode,
            gas_limit=25_000_000,
            gas_price=10,
            sender=sender,
        )

    @pytest.fixture
    def contract_creation_gas_cost(self, fork: Fork, opcode: Op) -> int:
        """Calculate gas cost of the contract creation operation."""
        gas_costs = fork.gas_costs()

        create_contract_base_gas = gas_costs.G_CREATE
        gas_opcode_gas = gas_costs.G_BASE
        push_dup_opcode_gas = gas_costs.G_VERY_LOW
        calldatasize_opcode_gas = gas_costs.G_BASE
        contract_creation_gas_usage = (
            create_contract_base_gas
            + gas_opcode_gas
            + (2 * push_dup_opcode_gas)
            + calldatasize_opcode_gas
        )
        if opcode == Op.CREATE2:  # Extra push operation
            contract_creation_gas_usage += push_dup_opcode_gas
        return contract_creation_gas_usage

    @pytest.fixture
    def initcode_word_cost(self, fork: Fork, initcode: Initcode) -> int:
        """Calculate gas cost charged for the initcode length."""
        gas_costs = fork.gas_costs()
        return ceiling_division(len(initcode), 32) * gas_costs.G_INITCODE_WORD

    @pytest.fixture
    def create2_word_cost(self, opcode: Op, fork: Fork, initcode: Initcode) -> int:
        """Calculate gas cost charged for the initcode length."""
        if opcode == Op.CREATE:
            return 0

        gas_costs = fork.gas_costs()
        return ceiling_division(len(initcode), 32) * gas_costs.G_KECCAK_256_WORD

    def test_create_opcode_initcode(
        self,
        state_test: StateTestFiller,
        env: Environment,
        pre: Alloc,
        post: Alloc,
        tx: Transaction,
        initcode: Initcode,
        caller_contract_address: Address,
        creator_contract_address: Address,
        created_contract_address: Address,
        contract_creation_gas_cost: int,
        initcode_word_cost: int,
        create2_word_cost: int,
        fork: Fork,
    ):
        """
        Test contract creation via the CREATE/CREATE2 opcodes that have an
        initcode that is on/over the max allowed limit.
        """
        if len(initcode) > fork.max_initcode_size():
            # Call returns 0 as out of gas s[0]==1
            post[caller_contract_address] = Account(
                nonce=1,
                storage={
                    0: 1,
                    1: 0,
                },
            )

            post[created_contract_address] = Account.NONEXISTENT
            post[creator_contract_address] = Account(
                nonce=1,
                storage={
                    0: 0,
                    1: 0,
                },
            )

        else:
            expected_gas_usage = contract_creation_gas_cost
            # The initcode is only executed if the length check succeeds
            expected_gas_usage += initcode.execution_gas
            # The code is only deployed if the length check succeeds
            expected_gas_usage += initcode.deployment_gas

            # CREATE2 hashing cost should only be deducted if the initcode
            # does not exceed the max length
            expected_gas_usage += create2_word_cost

            # Initcode word cost is only deducted if the length check
            # succeeds
            expected_gas_usage += initcode_word_cost

            # Call returns 1 as valid initcode length s[0]==1 && s[1]==1
            post[caller_contract_address] = Account(
                nonce=1,
                storage={
                    0: 0,
                    1: 1,
                },
            )

            post[created_contract_address] = Account(code=initcode.deploy_code)
            post[creator_contract_address] = Account(
                nonce=2,
                storage={
                    0: created_contract_address,
                    1: expected_gas_usage,
                },
            )

        state_test(
            env=env,
            pre=pre,
            post=post,
            tx=tx,
        )
