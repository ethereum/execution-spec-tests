"""Abstract base class for Ethereum forks."""

import re
from abc import ABC, ABCMeta, abstractmethod
from collections import defaultdict, deque
from typing import Any, ClassVar, List, Mapping, Optional, Protocol, Set, Sized, Tuple, Type

from semver import Version

from ethereum_test_base_types import AccessList, Address, BlobSchedule
from ethereum_test_base_types.conversions import BytesConvertible
from ethereum_test_vm import EVMCodeType, Opcodes

from .base_decorators import prefer_transition_to_method
from .gas_costs import GasCosts


class ForkAttribute(Protocol):
    """A protocol to get the attribute of a fork at a given block number and timestamp."""

    def __call__(self, block_number: int = 0, timestamp: int = 0) -> Any:
        """Return value of the attribute at the given block number and timestamp."""
        pass


class MemoryExpansionGasCalculator(Protocol):
    """A protocol to calculate the gas cost of memory expansion at a given fork."""

    def __call__(self, *, new_bytes: int, previous_bytes: int = 0) -> int:
        """Return gas cost of expanding the memory by the given length."""
        pass


class CalldataGasCalculator(Protocol):
    """A protocol to calculate the transaction gas cost of calldata at a given fork."""

    def __call__(self, *, data: BytesConvertible, floor: bool = False) -> int:
        """Return the transaction gas cost of calldata given its contents."""
        pass


class TransactionDataFloorCostCalculator(Protocol):
    """Calculate the transaction floor cost due to its calldata for a given fork."""

    def __call__(self, *, data: BytesConvertible) -> int:
        """Return transaction gas cost of calldata given its contents."""
        pass


class TransactionIntrinsicCostCalculator(Protocol):
    """A protocol to calculate the intrinsic gas cost of a transaction at a given fork."""

    def __call__(
        self,
        *,
        calldata: BytesConvertible = b"",
        contract_creation: bool = False,
        access_list: List[AccessList] | None = None,
        authorization_list_or_count: Sized | int | None = None,
        return_cost_deducted_prior_execution: bool = False,
    ) -> int:
        """
        Return the intrinsic gas cost of a transaction given its properties.

        Args:
            calldata: The data of the transaction.
            contract_creation: Whether the transaction creates a contract.
            access_list: The list of access lists for the transaction.
            authorization_list_or_count: The list of authorizations or the count of authorizations
                for the transaction.
            return_cost_deducted_prior_execution: If set to False, the returned value is equal to
                the minimum gas required for the transaction to be valid. If set to True, the
                returned value is equal to the cost that is deducted from the gas limit before
                the transaction starts execution.

        Returns:
            Gas cost of a transaction

        """
        pass


class BlobGasPriceCalculator(Protocol):
    """A protocol to calculate the blob gas price given the excess blob gas at a given fork."""

    def __call__(self, *, excess_blob_gas: int) -> int:
        """Return the blob gas price given the excess blob gas."""
        pass


class ExcessBlobGasCalculator(Protocol):
    """A protocol to calculate the excess blob gas for a block at a given fork."""

    def __call__(
        self,
        *,
        parent_excess_blob_gas: int | None = None,
        parent_excess_blobs: int | None = None,
        parent_blob_gas_used: int | None = None,
        parent_blob_count: int | None = None,
    ) -> int:
        """Return the excess blob gas given the parent's excess blob gas and blob gas used."""
        pass


class BaseForkMeta(ABCMeta):
    """Metaclass for BaseFork that manages fork registration and discovery."""

    _base_forks_registry: ClassVar[Set[Type["BaseFork"]]] = set()
    _transition_forks_registry: ClassVar[Set[Type["BaseFork"]]] = set()

    def __new__(cls, name, bases, namespace, **kwargs):
        """Create and register new fork classes."""
        new_class = super().__new__(cls, name, bases, namespace, **kwargs)
        if getattr(new_class, "__abstractmethods__", False):
            return new_class
        if new_class.__name__ == "NewTransitionClass" and any(
            base.__name__ == "TransitionBaseClass" for base in bases
        ):
            cls._transition_forks_registry.add(new_class)
        elif not is_transition_fork_by_heuristic(new_class.__name__):
            if new_class.__name__ == "Prague":
                print(new_class.__name__, bases, namespace)
            cls._base_forks_registry.add(new_class)

        return new_class

    @classmethod
    def forks(cls, fork_type: str = "all") -> List[Type["BaseFork"]]:
        """
        Return an ordered list of forks, maintaining chronological order from Frontier.
        Set `fork_type` to "base" to get only base forks, "transition" for transition forks.
        """
        if fork_type == "base":
            selected = list(cls._base_forks_registry)
        elif fork_type == "transition":
            selected = list(cls._transition_forks_registry)
        elif fork_type == "all":
            selected = list(cls._base_forks_registry | cls._transition_forks_registry)
        else:
            raise ValueError(f"Unknown fork_type: {fork_type!r}")

        # Build dependency graph for topological sorting
        graph = defaultdict(list)
        in_degree = {fork: 0 for fork in selected}
        for fork in selected:
            parent = fork.parent()
            if parent and parent in selected:
                graph[parent].append(fork)
                in_degree[fork] += 1

        frontier_candidates = [f for f in selected if in_degree[f] == 0]
        if not frontier_candidates:
            raise ValueError("No starting fork found - circular dependency detected")
        queue = deque(sorted(frontier_candidates, key=lambda f: len(f.__mro__)))

        # Perform topological sort maintaining chronological order
        result: List[Type["BaseFork"]] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            children = sorted(graph[node], key=lambda f: f.name())
            for child in children:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        return result

    def __repr__(cls) -> str:
        """Print the name of the fork, instead of the class."""
        return cls.name()

    @staticmethod
    def _maybe_transitioned(fork_cls: "BaseForkMeta") -> "BaseForkMeta":
        """Return the transitioned fork, if a transition fork, otherwise return `fork_cls`."""
        return fork_cls.transitions_to() if hasattr(fork_cls, "transitions_to") else fork_cls

    @staticmethod
    def _is_subclass_of(a: "BaseForkMeta", b: "BaseForkMeta") -> bool:
        """Check if `a` is a subclass of `b`, taking fork transitions into account."""
        a = BaseForkMeta._maybe_transitioned(a)
        b = BaseForkMeta._maybe_transitioned(b)
        return issubclass(a, b)

    def __gt__(cls, other: "BaseForkMeta") -> bool:
        """Compare if a fork is newer than some other fork (cls > other)."""
        return cls is not other and BaseForkMeta._is_subclass_of(cls, other)

    def __ge__(cls, other: "BaseForkMeta") -> bool:
        """Compare if a fork is newer than or equal to some other fork (cls >= other)."""
        return cls is other or BaseForkMeta._is_subclass_of(cls, other)

    def __lt__(cls, other: "BaseForkMeta") -> bool:
        """Compare if a fork is older than some other fork (cls < other)."""
        # "Older" means other is a subclass of cls, but not the same.
        return cls is not other and BaseForkMeta._is_subclass_of(other, cls)

    def __le__(cls, other: "BaseForkMeta") -> bool:
        """Compare if a fork is older than or equal to some other fork (cls <= other)."""
        return cls is other or BaseForkMeta._is_subclass_of(other, cls)


class BaseFork(ABC, metaclass=BaseForkMeta):
    """
    An abstract class representing an Ethereum fork.

    Must contain all the methods used by every fork.
    """

    _transition_tool_name: ClassVar[Optional[str]] = None
    _blockchain_test_network_name: ClassVar[Optional[str]] = None
    _solc_name: ClassVar[Optional[str]] = None
    _ignore: ClassVar[bool] = False

    def __init_subclass__(
        cls,
        *,
        transition_tool_name: Optional[str] = None,
        blockchain_test_network_name: Optional[str] = None,
        solc_name: Optional[str] = None,
        ignore: bool = False,
    ) -> None:
        """Initialize new fork with values that don't carry over to subclass forks."""
        cls._transition_tool_name = transition_tool_name
        cls._blockchain_test_network_name = blockchain_test_network_name
        cls._solc_name = solc_name
        cls._ignore = ignore

    @classmethod
    def name(cls) -> str:
        """Return name of the fork."""
        return cls.__name__

    @classmethod
    def fork_at(cls, block_number: int = 0, timestamp: int = 0) -> Type["BaseFork"]:
        """
        Return fork at the given block number and timestamp.
        Useful only for transition forks, and it's a no-op for normal forks.
        """
        return cls

    @classmethod
    @abstractmethod
    def transition_tool_name(cls, block_number: int = 0, timestamp: int = 0) -> str:
        """Return fork name as it's meant to be passed to the transition tool for execution."""
        pass

    @classmethod
    @abstractmethod
    def solc_name(cls) -> str:
        """Return fork name as it's meant to be passed to the solc compiler."""
        pass

    @classmethod
    @abstractmethod
    def solc_min_version(cls) -> Version:
        """Return minimum version of solc that supports this fork."""
        pass

    @classmethod
    def blockchain_test_network_name(cls) -> str:
        """Return network configuration name to be used in BlockchainTests for this fork."""
        if cls._blockchain_test_network_name is not None:
            return cls._blockchain_test_network_name
        return cls.name()

    @classmethod
    def is_deployed(cls) -> bool:
        """
        Return whether the fork has been deployed to mainnet, or not.

        Must be overridden and return False for forks that are still under
        development.
        """
        return True

    @classmethod
    def ignore(cls) -> bool:
        """Return whether the fork should be ignored during test generation."""
        return cls._ignore

    @classmethod
    def parent(cls) -> Type["BaseFork"] | None:
        """Return the parent fork."""
        base_class = cls.__bases__[0]
        assert issubclass(base_class, BaseFork)
        if base_class == BaseFork:
            return None
        return base_class

    @classmethod
    @abstractmethod
    def get_reward(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return expected reward amount in wei."""
        pass

    @classmethod
    @abstractmethod
    def header_base_fee_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain base fee."""
        pass

    @classmethod
    @abstractmethod
    def header_prev_randao_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain prev randao value."""
        pass

    @classmethod
    @abstractmethod
    def header_zero_difficulty_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must have difficulty zero."""
        pass

    @classmethod
    @abstractmethod
    def header_withdrawals_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain withdrawals."""
        pass

    @classmethod
    @abstractmethod
    def header_excess_blob_gas_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain excess blob gas."""
        pass

    @classmethod
    @abstractmethod
    def header_blob_gas_used_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain blob gas used."""
        pass

    @classmethod
    @abstractmethod
    def header_beacon_root_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain parent beacon block root."""
        pass

    @classmethod
    @abstractmethod
    def header_requests_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return true if the header must contain beacon chain requests."""
        pass

    @classmethod
    @abstractmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """Return dataclass with the gas costs constants."""
        pass

    @classmethod
    @abstractmethod
    def memory_expansion_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> MemoryExpansionGasCalculator:
        """Return a callable that calculates the gas cost of memory expansion."""
        pass

    @classmethod
    @abstractmethod
    def calldata_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> CalldataGasCalculator:
        """
        Return callable that calculates the transaction gas cost for its calldata
        depending on its contents.
        """
        pass

    @classmethod
    @abstractmethod
    def transaction_data_floor_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionDataFloorCostCalculator:
        """Return a callable that calculates the transaction floor cost due to its calldata."""
        pass

    @classmethod
    @abstractmethod
    def transaction_intrinsic_cost_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> TransactionIntrinsicCostCalculator:
        """Return callable that calculates the intrinsic gas cost of a transaction."""
        pass

    @classmethod
    @abstractmethod
    def blob_gas_price_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> BlobGasPriceCalculator:
        """Return a callable that calculates the blob gas price."""
        pass

    @classmethod
    @abstractmethod
    def excess_blob_gas_calculator(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> ExcessBlobGasCalculator:
        """Return a callable that calculates the excess blob gas."""
        pass

    @classmethod
    @abstractmethod
    def min_base_fee_per_blob_gas(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the minimum base fee per blob gas."""
        pass

    @classmethod
    @abstractmethod
    def blob_gas_per_blob(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the amount of blob gas used per blob."""
        pass

    @classmethod
    @abstractmethod
    def blob_base_fee_update_fraction(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the blob base fee update fraction."""
        pass

    @classmethod
    @abstractmethod
    def supports_blobs(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Return whether blobs are supported or not."""
        pass

    @classmethod
    @abstractmethod
    def target_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the target blobs per block."""
        pass

    @classmethod
    @abstractmethod
    def max_blobs_per_block(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Return the max blobs per block."""
        pass

    @classmethod
    @prefer_transition_to_method
    @abstractmethod
    def blob_schedule(cls, block_number: int = 0, timestamp: int = 0) -> Optional[BlobSchedule]:
        """Return the blob schedule."""
        pass

    @classmethod
    @abstractmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """Return list of the supported transaction types."""
        pass

    @classmethod
    @abstractmethod
    def contract_creating_tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """Return list of the supported transaction types that can create contracts."""
        pass

    @classmethod
    @abstractmethod
    def max_request_type(cls, block_number: int = 0, timestamp: int = 0) -> Optional[int]:
        """Return max request type supported by the fork."""
        pass

    @classmethod
    @abstractmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return list of the supported precompiles."""
        pass

    @classmethod
    @abstractmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return list of the supported system contracts."""
        pass

    @classmethod
    @prefer_transition_to_method
    @abstractmethod
    def pre_allocation(cls) -> Mapping:
        """
        Return required pre-allocation of accounts for any kind of test.

        This method must always call the `fork_to` method when transitioning, because the
        allocation can only be set at genesis, and thus cannot be changed at transition time.
        """
        pass

    @classmethod
    @prefer_transition_to_method
    @abstractmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """
        Return required pre-allocation of accounts for any blockchain tests.

        This method must always call the `fork_to` method when transitioning, because the
        allocation can only be set at genesis, and thus cannot be changed at transition time.
        """
        pass

    @classmethod
    @abstractmethod
    def evm_code_types(cls, block_number: int = 0, timestamp: int = 0) -> List[EVMCodeType]:
        """Return list of EVM code types."""
        pass

    @classmethod
    @abstractmethod
    def call_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """Return list of tuples with the call opcodes and its corresponding EVM code type."""
        pass

    @classmethod
    @abstractmethod
    def valid_opcodes(
        cls,
    ) -> List[Opcodes]:
        """Return list of supported opcodes."""
        pass

    @classmethod
    @abstractmethod
    def create_opcodes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> List[Tuple[Opcodes, EVMCodeType]]:
        """Return list of tuples with the create opcodes and its corresponding EVM code type."""
        pass

    # Engine API information abstract methods
    @classmethod
    @abstractmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """Return engine api new payload version."""
        pass

    @classmethod
    @abstractmethod
    def engine_get_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """Return engine api get payload version."""
        pass

    @classmethod
    @abstractmethod
    def engine_forkchoice_updated_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """Return engine api forkchoice updated version."""
        pass

    @classmethod
    @abstractmethod
    def engine_new_payload_blob_hashes(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api new payload calls should include blob hashes."""
        pass

    @classmethod
    @abstractmethod
    def engine_new_payload_beacon_root(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api new payload calls should include a beacon block root."""
        pass

    @classmethod
    @abstractmethod
    def engine_new_payload_requests(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api new payload calls should include target blobs per block."""
        pass

    @classmethod
    @abstractmethod
    def engine_new_payload_target_blobs_per_block(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api new payload calls should include target blobs per block."""
        pass

    @classmethod
    @abstractmethod
    def engine_payload_attribute_target_blobs_per_block(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api payload attributes should include target blobs per block."""
        pass

    @classmethod
    @abstractmethod
    def engine_payload_attribute_max_blobs_per_block(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[bool]:
        """Return whether engine api payload attributes should include max blobs per block."""
        pass


class GenesisBaseFork(BaseFork):
    """
    Implements all abstract methods from BaseFork with defaults.
    Frontier must inherit from this class.
    """

    @classmethod
    def get_reward(cls, block_number=0, timestamp=0) -> int:
        """Return expected reward amount in wei of a given fork. Default is 0."""
        return 0

    @classmethod
    def header_base_fee_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain base fee. Default is False."""
        return False

    @classmethod
    def header_prev_randao_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain prev randao value. Default is False."""
        return False

    @classmethod
    def header_zero_difficulty_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must have difficulty zero. Default is False."""
        return False

    @classmethod
    def header_withdrawals_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain withdrawals. Default is False."""
        return False

    @classmethod
    def header_excess_blob_gas_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain excess blob gas. Default is False."""
        return False

    @classmethod
    def header_blob_gas_used_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain blob gas used. Default is False."""
        return False

    @classmethod
    def header_beacon_root_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain parent beacon block root. Default is False."""
        return False

    @classmethod
    def header_requests_required(cls, block_number=0, timestamp=0) -> bool:
        """Return true if the header must contain beacon chain requests. Default is False."""
        return False

    @classmethod
    def gas_costs(cls, block_number=0, timestamp=0) -> GasCosts:
        """Return dataclass with the gas costs constants. Default is empty `GasCosts` dataclass."""
        return GasCosts()

    @classmethod
    def memory_expansion_gas_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> MemoryExpansionGasCalculator:
        """
        Return a callable that calculates the gas cost of memory expansion.
        Default callable returns 0.
        """

        def fn(*, new_bytes: int, previous_bytes: int = 0) -> int:
            return 0

        return fn

    @classmethod
    def calldata_gas_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> CalldataGasCalculator:
        """
        Return a callable that calculates the transaction gas cost for its calldata
        depending on its contexts. Default callable returns 0.
        """

        def fn(*, data: BytesConvertible, floor: bool = False) -> int:
            return 0

        return fn

    @classmethod
    def transaction_data_floor_cost_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> TransactionDataFloorCostCalculator:
        """
        Return a callable that calculates the transaction floor cost due to its calldata.
        Default callable returns 0.
        """

        def fn(*, data: BytesConvertible) -> int:
            return 0

        return fn

    @classmethod
    def transaction_intrinsic_cost_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> TransactionIntrinsicCostCalculator:
        """
        Return a callable that calculates the intrinsic gas cost of a transaction.
        Default callable returns 0.
        """

        def fn(
            *,
            calldata: BytesConvertible = b"",
            contract_creation: bool = False,
            access_list: List[AccessList] | None = None,
            authorization_list_or_count: Sized | int | None = None,
            return_cost_deducted_prior_execution: bool = False,
        ) -> int:
            return 0

        return fn

    @classmethod
    def blob_gas_price_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> BlobGasPriceCalculator:
        """Return a callable that calculates the blob gas price. Default raises an error."""
        raise NotImplementedError(f"Blob gas price calculator is not supported in {cls.name()}")

    @classmethod
    def excess_blob_gas_calculator(
        cls,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> ExcessBlobGasCalculator:
        """Return a callable that calculates the excess blob gas. Default callable returns 0."""

        def fn(
            *,
            parent_excess_blob_gas: int | None = None,
            parent_excess_blobs: int | None = None,
            parent_blob_gas_used: int | None = None,
            parent_blob_count: int | None = None,
        ) -> int:
            return 0

        return fn

    @classmethod
    def min_base_fee_per_blob_gas(cls, block_number=0, timestamp=0) -> int:
        """Return the minimum base fee per blob gas. Default is 0."""
        return 0

    @classmethod
    def blob_gas_per_blob(cls, block_number=0, timestamp=0) -> int:
        """Return the amount of blob gas used per blob. Default is 0."""
        return 0

    @classmethod
    def blob_base_fee_update_fraction(cls, block_number=0, timestamp=0) -> int:
        """Return the blob base fee update fraction. Default is 0."""
        return 0

    @classmethod
    def supports_blobs(cls, block_number=0, timestamp=0) -> bool:
        """Return whether blobs are supported or not. Default is False."""
        return False

    @classmethod
    def target_blobs_per_block(cls, block_number=0, timestamp=0) -> int:
        """Return the target blobs per block. Default is 0."""
        return 0

    @classmethod
    def max_blobs_per_block(cls, block_number=0, timestamp=0) -> int:
        """Return the max blobs per block. Default is 0."""
        return 0

    @classmethod
    def blob_schedule(cls, block_number=0, timestamp=0) -> Optional[BlobSchedule]:
        """Return the blob schedule. Default is `None`."""
        return None

    @classmethod
    def max_request_type(cls, block_number=0, timestamp=0) -> Optional[int]:
        """Return max request type supported by the fork. Default is `None`."""
        return None

    @classmethod
    def tx_types(cls, block_number=0, timestamp=0) -> List[int]:
        """Return list of the supported transaction types. Default is empty."""
        return []

    @classmethod
    def contract_creating_tx_types(cls, block_number=0, timestamp=0) -> List[int]:
        """
        Return list of the supported transaction types that can create contracts.
        Default is empty.
        """
        return []

    @classmethod
    def precompiles(cls, block_number=0, timestamp=0) -> List[Address]:
        """Return list of the supported precompiles. Default is empty."""
        return []

    @classmethod
    def system_contracts(cls, block_number=0, timestamp=0) -> List[Address]:
        """Return list of the supported system contracts. Default is empty."""
        return []

    @classmethod
    def pre_allocation(cls) -> Mapping:
        """Return required pre-allocation of accounts for any kind of test. Default is empty."""
        return {}

    @classmethod
    def pre_allocation_blockchain(cls) -> Mapping:
        """
        Return required pre-allocation of accounts for any blockchain tests.
        Default is empty.
        """
        return {}

    @classmethod
    def evm_code_types(cls, block_number=0, timestamp=0) -> List[EVMCodeType]:
        """Return list of EVM code types. Default is empty."""
        return []

    @classmethod
    def call_opcodes(cls, block_number=0, timestamp=0) -> List[Tuple[Opcodes, EVMCodeType]]:
        """
        Return list of tuples with the call opcodes and its corresponding EVM code type.
        Default is empty.
        """
        return []

    @classmethod
    def valid_opcodes(cls) -> List[Opcodes]:
        """Return list of of supported opcodes. Default is empty."""
        return []

    @classmethod
    def create_opcodes(cls, block_number=0, timestamp=0) -> List[Tuple[Opcodes, EVMCodeType]]:
        """
        Return list of tuples with the create opcodes and its corresponding EVM code type.
        Default is empty.
        """
        return []

    # Engine API information default methods
    @classmethod
    def engine_new_payload_version(cls, block_number=0, timestamp=0) -> Optional[int]:
        """Return engine api new payload version. Default is `None`."""
        return None

    @classmethod
    def engine_get_payload_version(cls, block_number=0, timestamp=0) -> Optional[int]:
        """Return engine api get payload version. Default is `None`."""
        return None

    @classmethod
    def engine_forkchoice_updated_version(cls, block_number=0, timestamp=0) -> Optional[int]:
        """Return engine api forkchoice updated version. Default is `None`."""
        return None

    @classmethod
    def engine_new_payload_blob_hashes(cls, block_number=0, timestamp=0) -> Optional[bool]:
        """
        Return whether engine api new payload calls should include blob hashes.
        Default is `None`.
        """
        return None

    @classmethod
    def engine_new_payload_beacon_root(cls, block_number=0, timestamp=0) -> Optional[bool]:
        """
        Return whether engine api new payload calls should include a beacon block root.
        Default is `None`.
        """
        return None

    @classmethod
    def engine_new_payload_requests(cls, block_number=0, timestamp=0) -> Optional[bool]:
        """
        Return whether engine api new payload calls should include requests.
        Default is `None`.
        """
        return None

    @classmethod
    def engine_new_payload_target_blobs_per_block(
        cls, block_number=0, timestamp=0
    ) -> Optional[bool]:
        """
        Return whether engine api new payload calls should include target blobs per block.
        Default is `None`.
        """
        return None

    @classmethod
    def engine_payload_attribute_target_blobs_per_block(
        cls, block_number=0, timestamp=0
    ) -> Optional[bool]:
        """
        Return whether engine api payload attributes should include target blobs per block.
        Default is `None`.
        """
        return None

    @classmethod
    def engine_payload_attribute_max_blobs_per_block(
        cls, block_number=0, timestamp=0
    ) -> Optional[bool]:
        """
        Return whether engine api payload attributes should include max blobs per block.
        Default is `None`.
        """
        return None


# Fork Type Alias
Fork = Type[BaseFork]


def is_transition_fork_by_heuristic(name: str) -> bool:
    """Return True if 'name' strongly suggests a 'transition' fork."""
    segments = re.findall(r"[A-Z][a-z0-9]*", name)
    if len(segments) < 3:
        return False
    middle = segments[1:-1]
    bridge_tokens = {"To", "At", "From"}
    if not any(s in bridge_tokens for s in middle):
        return False
    return True
