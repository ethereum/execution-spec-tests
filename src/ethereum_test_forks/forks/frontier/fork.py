"""Frontier fork definition."""

from typing import List, Mapping, Optional, Sized, Tuple

from semver import Version

from ethereum_test_base_types import AccessList, Address, BlobSchedule, Bytes
from ethereum_test_base_types.conversions import BytesConvertible
from ethereum_test_forks.base_fork import (
    BaseFork,
    BlobGasPriceCalculator,
    CalldataGasCalculator,
    ExcessBlobGasCalculator,
    MemoryExpansionGasCalculator,
    TransactionDataFloorCostCalculator,
    TransactionIntrinsicCostCalculator,
)
from ethereum_test_forks.gas_costs import GasCosts
from ethereum_test_forks.helpers import ceiling_division
from ethereum_test_vm import EVMCodeType, Opcodes


class Frontier(BaseFork, solc_name="homestead"):
    """Frontier fork."""

    @classmethod
    def transition_tool_name(cls, block_number: int = 0, timestamp: int = 0) -> str:
        """Return fork name as it's meant to be passed to the transition tool for execution."""
        if cls._transition_tool_name is not None:
            return cls._transition_tool_name
        return cls.name()

    @classmethod
    def solc_name(cls) -> str:
        """Return fork name as it's meant to be passed to the solc compiler."""
        if cls._solc_name is not None:
            return cls._solc_name
        return cls.name().lower()

    @classmethod
    def solc_min_version(cls) -> Version:
        """Return minimum version of solc that supports this fork."""
        return Version.parse("0.8.20")

    @classmethod
    def header_base_fee_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain base fee."""
        return False

    @classmethod
    def header_prev_randao_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain Prev Randao value."""
        return False

    @classmethod
    def header_zero_difficulty_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not have difficulty zero."""
        return False

    @classmethod
    def header_withdrawals_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain withdrawals."""
        return False

    @classmethod
    def header_excess_blob_gas_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain excess blob gas."""
        return False

    @classmethod
    def header_blob_gas_used_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain blob gas used."""
        return False

    @classmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """Return dataclass with the defined gas costs constants for genesis."""
        return GasCosts(
            G_JUMPDEST=1,
            G_BASE=2,
            G_VERY_LOW=3,
            G_LOW=5,
            G_MID=8,
            G_HIGH=10,
            G_WARM_ACCOUNT_ACCESS=100,
            G_COLD_ACCOUNT_ACCESS=2_600,
            G_ACCESS_LIST_ADDRESS=2_400,
            G_ACCESS_LIST_STORAGE=1_900,
            G_WARM_SLOAD=100,
            G_COLD_SLOAD=2_100,
            G_STORAGE_SET=20_000,
            G_STORAGE_RESET=2_900,
            R_STORAGE_CLEAR=4_800,
            G_SELF_DESTRUCT=5_000,
            G_CREATE=32_000,
            G_CODE_DEPOSIT_BYTE=200,
            G_INITCODE_WORD=2,
            G_CALL_VALUE=9_000,
            G_CALL_STIPEND=2_300,
            G_NEW_ACCOUNT=25_000,
            G_EXP=10,
            G_EXP_BYTE=50,
            G_MEMORY=3,
            G_TX_DATA_ZERO=4,
            G_TX_DATA_NON_ZERO=68,
            G_TX_DATA_STANDARD_TOKEN_COST=0,
            G_TX_DATA_FLOOR_TOKEN_COST=0,
            G_TRANSACTION=21_000,
            G_TRANSACTION_CREATE=32_000,
            G_LOG=375,
            G_LOG_DATA=8,
            G_LOG_TOPIC=375,
            G_KECCAK_256=30,
            G_KECCAK_256_WORD=6,
            G_COPY=3,
            G_BLOCKHASH=20,
            G_AUTHORIZATION=0,
            R_AUTHORIZATION_EXISTING_AUTHORITY=0,
        )

    @classmethod
    def memory_expansion_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> MemoryExpansionGasCalculator:
        """Return callable that calculates the gas cost of memory expansion for the fork."""
        gas_costs = cls.gas_costs(block_number, timestamp)

        def fn(*, new_bytes: int, previous_bytes: int = 0) -> int:
            if new_bytes <= previous_bytes:
                return 0
            new_words = ceiling_division(new_bytes, 32)
            previous_words = ceiling_division(previous_bytes, 32)

            def c(w: int) -> int:
                return (gas_costs.G_MEMORY * w) + ((w * w) // 512)

            return c(new_words) - c(previous_words)

        return fn

    @classmethod
    def calldata_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> CalldataGasCalculator:
        """
        Return callable that calculates the transaction gas cost for its calldata
        depending on its contents.
        """
        gas_costs = cls.gas_costs(block_number, timestamp)

        def fn(*, data: BytesConvertible, floor: bool = False) -> int:
            cost = 0
            for b in Bytes(data):
                if b == 0:
                    cost += gas_costs.G_TX_DATA_ZERO
                else:
                    cost += gas_costs.G_TX_DATA_NON_ZERO
            return cost

        return fn

    @classmethod
    def transaction_data_floor_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionDataFloorCostCalculator:
        """At frontier, the transaction data floor cost is a constant zero."""

        def fn(*, data: BytesConvertible) -> int:
            return 0

        return fn

    @classmethod
    def transaction_intrinsic_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionIntrinsicCostCalculator:
        """Return callable that calculates the intrinsic gas cost of a transaction for the fork."""
        gas_costs = cls.gas_costs(block_number, timestamp)
        calldata_gas_calculator = cls.calldata_gas_calculator(block_number, timestamp)

        def fn(
            *,
            calldata: BytesConvertible = b"",
            contract_creation: bool = False,
            access_list: List[AccessList] | None = None,
            authorization_list_or_count: Sized | int | None = None,
            return_cost_deducted_prior_execution: bool = False,
        ) -> int:
            assert access_list is None, f"Access list is not supported in {cls.name()}"
            assert authorization_list_or_count is None, (
                f"Authorizations are not supported in {cls.name()}"
            )
            intrinsic_cost: int = gas_costs.G_TRANSACTION

            if contract_creation:
                intrinsic_cost += gas_costs.G_INITCODE_WORD * ceiling_division(
                    len(Bytes(calldata)), 32
                )

            return intrinsic_cost + calldata_gas_calculator(data=calldata)

        return fn

    @classmethod
    def blob_gas_price_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> BlobGasPriceCalculator:
        """Return a callable that calculates the blob gas price at a given fork."""
        raise NotImplementedError(f"Blob gas price calculator is not supported in {cls.name()}")

    @classmethod
    def excess_blob_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> ExcessBlobGasCalculator:
        """Return a callable that calculates the excess blob gas for a block at a given fork."""
        raise NotImplementedError(f"Excess blob gas calculator is not supported in {cls.name()}")

    @classmethod
    def min_base_fee_per_blob_gas(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the amount of blob gas used per blob at a given fork."""
        raise NotImplementedError(f"Base fee per blob gas is not supported in {cls.name()}")

    @classmethod
    def blob_base_fee_update_fraction(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the blob base fee update fraction at a given fork."""
        raise NotImplementedError(
            f"Blob base fee update fraction is not supported in {cls.name()}"
        )

    @classmethod
    def blob_gas_per_blob(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the amount of blob gas used per blob at a given fork."""
        return 0

    @classmethod
    def supports_blobs(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Blobs are not supported at Frontier."""
        return False

    @classmethod
    def target_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the target number of blobs per block at a given fork."""
        raise NotImplementedError(f"Target blobs per block is not supported in {cls.name()}")

    @classmethod
    def max_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the max number of blobs per block at a given fork."""
        raise NotImplementedError(f"Max blobs per block is not supported in {cls.name()}")

    @classmethod
    def blob_schedule(cls, block_number: int = 0, timestamp: int = 0) -> BlobSchedule | None:
        """At genesis, no blob schedule is used."""
        return None

    @classmethod
    def header_requests_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain beacon chain requests."""
        return False

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """At genesis, payloads cannot be sent through the engine API."""
        return None

    @classmethod
    def header_beacon_root_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, header must not contain parent beacon block root."""
        return False

    @classmethod
    def engine_new_payload_blob_hashes(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, payloads do not have blob hashes."""
        return False

    @classmethod
    def engine_new_payload_beacon_root(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, payloads do not have a parent beacon block root."""
        return False

    @classmethod
    def engine_new_payload_requests(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """At genesis, payloads do not have requests."""
        return False

    @classmethod
    def engine_new_payload_target_blobs_per_block(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> bool:
        """At genesis, payloads do not have target blobs per block."""
        return False

    @classmethod
    def engine_payload_attribute_target_blobs_per_block(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> bool:
        """At genesis, payload attributes do not include the target blobs per block."""
        return False

    @classmethod
    def engine_payload_attribute_max_blobs_per_block(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> bool:
        """At genesis, payload attributes do not include the max blobs per block."""
        return False

    @classmethod
    def engine_forkchoice_updated_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """At genesis, forkchoice updates cannot be sent through the engine API."""
        return cls.engine_new_payload_version(block_number, timestamp)

    @classmethod
    def engine_get_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """At genesis, payloads cannot be retrieved through the engine API."""
        return cls.engine_new_payload_version(block_number, timestamp)

    @classmethod
    def get_reward(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """
        At Genesis the expected reward amount in wei is
        5_000_000_000_000_000_000.
        """
        return 5_000_000_000_000_000_000

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At Genesis, only legacy transactions are allowed."""
        return [0]

    @classmethod
    def contract_creating_tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """At Genesis, only legacy transactions are allowed."""
        return [0]

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """At Genesis, no pre-compiles are present."""
        return []

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """At Genesis, no system-contracts are present."""
        return []

    @classmethod
    def evm_code_types(cls, block_number: int = 0, timestamp: int = 0) -> List[EVMCodeType]:
        """At Genesis, only legacy EVM code is supported."""
        return [EVMCodeType.LEGACY]

    @classmethod
    def call_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """Return list of call opcodes supported by the fork."""
        return [
            (Opcodes.CALL, EVMCodeType.LEGACY),
            (Opcodes.CALLCODE, EVMCodeType.LEGACY),
        ]

    @classmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of Opcodes that are valid to work on this fork."""
        return [
            Opcodes.STOP,
            Opcodes.ADD,
            Opcodes.MUL,
            Opcodes.SUB,
            Opcodes.DIV,
            Opcodes.SDIV,
            Opcodes.MOD,
            Opcodes.SMOD,
            Opcodes.ADDMOD,
            Opcodes.MULMOD,
            Opcodes.EXP,
            Opcodes.SIGNEXTEND,
            Opcodes.LT,
            Opcodes.GT,
            Opcodes.SLT,
            Opcodes.SGT,
            Opcodes.EQ,
            Opcodes.ISZERO,
            Opcodes.AND,
            Opcodes.OR,
            Opcodes.XOR,
            Opcodes.NOT,
            Opcodes.BYTE,
            Opcodes.SHA3,
            Opcodes.ADDRESS,
            Opcodes.BALANCE,
            Opcodes.ORIGIN,
            Opcodes.CALLER,
            Opcodes.CALLVALUE,
            Opcodes.CALLDATALOAD,
            Opcodes.CALLDATASIZE,
            Opcodes.CALLDATACOPY,
            Opcodes.CODESIZE,
            Opcodes.CODECOPY,
            Opcodes.GASPRICE,
            Opcodes.EXTCODESIZE,
            Opcodes.EXTCODECOPY,
            Opcodes.BLOCKHASH,
            Opcodes.COINBASE,
            Opcodes.TIMESTAMP,
            Opcodes.NUMBER,
            Opcodes.PREVRANDAO,
            Opcodes.GASLIMIT,
            Opcodes.POP,
            Opcodes.MLOAD,
            Opcodes.MSTORE,
            Opcodes.MSTORE8,
            Opcodes.SLOAD,
            Opcodes.SSTORE,
            Opcodes.PC,
            Opcodes.MSIZE,
            Opcodes.GAS,
            Opcodes.JUMP,
            Opcodes.JUMPI,
            Opcodes.JUMPDEST,
            Opcodes.PUSH1,
            Opcodes.PUSH2,
            Opcodes.PUSH3,
            Opcodes.PUSH4,
            Opcodes.PUSH5,
            Opcodes.PUSH6,
            Opcodes.PUSH7,
            Opcodes.PUSH8,
            Opcodes.PUSH9,
            Opcodes.PUSH10,
            Opcodes.PUSH11,
            Opcodes.PUSH12,
            Opcodes.PUSH13,
            Opcodes.PUSH14,
            Opcodes.PUSH15,
            Opcodes.PUSH16,
            Opcodes.PUSH17,
            Opcodes.PUSH18,
            Opcodes.PUSH19,
            Opcodes.PUSH20,
            Opcodes.PUSH21,
            Opcodes.PUSH22,
            Opcodes.PUSH23,
            Opcodes.PUSH24,
            Opcodes.PUSH25,
            Opcodes.PUSH26,
            Opcodes.PUSH27,
            Opcodes.PUSH28,
            Opcodes.PUSH29,
            Opcodes.PUSH30,
            Opcodes.PUSH31,
            Opcodes.PUSH32,
            Opcodes.DUP1,
            Opcodes.DUP2,
            Opcodes.DUP3,
            Opcodes.DUP4,
            Opcodes.DUP5,
            Opcodes.DUP6,
            Opcodes.DUP7,
            Opcodes.DUP8,
            Opcodes.DUP9,
            Opcodes.DUP10,
            Opcodes.DUP11,
            Opcodes.DUP12,
            Opcodes.DUP13,
            Opcodes.DUP14,
            Opcodes.DUP15,
            Opcodes.DUP16,
            Opcodes.SWAP1,
            Opcodes.SWAP2,
            Opcodes.SWAP3,
            Opcodes.SWAP4,
            Opcodes.SWAP5,
            Opcodes.SWAP6,
            Opcodes.SWAP7,
            Opcodes.SWAP8,
            Opcodes.SWAP9,
            Opcodes.SWAP10,
            Opcodes.SWAP11,
            Opcodes.SWAP12,
            Opcodes.SWAP13,
            Opcodes.SWAP14,
            Opcodes.SWAP15,
            Opcodes.SWAP16,
            Opcodes.LOG0,
            Opcodes.LOG1,
            Opcodes.LOG2,
            Opcodes.LOG3,
            Opcodes.LOG4,
            Opcodes.CREATE,
            Opcodes.CALL,
            Opcodes.CALLCODE,
            Opcodes.RETURN,
            Opcodes.SELFDESTRUCT,
        ]

    @classmethod
    def create_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """At Genesis, only `CREATE` opcode is supported."""
        return [
            (Opcodes.CREATE, EVMCodeType.LEGACY),
        ]

    @classmethod
    def max_request_type(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """At genesis, no request type is supported, signaled by -1."""
        return -1

    @classmethod
    def pre_allocation(cls) -> Mapping:
        """
        Return whether the fork expects pre-allocation of accounts.

        Frontier does not require pre-allocated accounts
        """
        return {}

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """
        Return whether the fork expects pre-allocation of accounts.

        Frontier does not require pre-allocated accounts
        """
        return {}
