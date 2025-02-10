"""Base class for Ethereum Improvement Proposals (EIPs)."""

from abc import ABC, ABCMeta
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Type

from ethereum_test_base_types import Address

from .gas_costs import GasCosts


class EIPAttribute(Protocol):
    """A protocol to get an attribute of an EIP at a given block number and timestamp."""

    def __call__(self, block_number: int = 0, timestamp: int = 0) -> Any:
        """Return value of the attribute at the given block number and timestamp."""
        pass


class BaseEIPMeta(ABCMeta):
    """
    Metaclass for BaseEIP.
    Maintains a registry of EIPs keyed by their integer ID.
    """

    _registry: Dict[int, Type["BaseEIP"]] = {}

    @property
    def eip_id(cls) -> int:
        """
        Extract the EIP number from the class name (by parsing out digits).
        Override this if your EIP class name is not EIP-<digits>.
        """
        return int("".join(filter(str.isdigit, cls.__name__)))

    def __repr__(cls) -> str:
        """Print the EIP ID instead of the class name."""
        return f"EIP-{cls.eip_id}"

    @classmethod
    def get_eip(mcs, eip_id: int) -> Optional[Type["BaseEIP"]]:
        """Get an EIP implementation by its ID."""
        return mcs._registry.get(eip_id)

    @classmethod
    def get_all_eips(mcs) -> Dict[int, Type["BaseEIP"]]:
        """Get all registered EIPs."""
        return mcs._registry.copy()

    @classmethod
    def register_eip(mcs, eip_cls: Type["BaseEIP"]) -> None:
        """Register an EIP implementation."""
        mcs._registry[eip_cls.eip_id] = eip_cls


class BaseEIP(ABC, metaclass=BaseEIPMeta):
    """
    Abstract base class for Ethereum Improvement Proposals (EIPs).
    Each EIP implementation should inherit from this class and
    implement the relevant methods for that specific EIP's functionality.
    """

    _fork: ClassVar[Optional[str]] = None

    def __init_subclass__(cls, *, fork: Optional[str] = None) -> None:
        """Initialize new EIP and register it in the registry."""
        cls._fork = fork
        BaseEIPMeta.register_eip(cls)

    @classmethod
    def fork_name(cls) -> Optional[str]:
        """Return the name of the fork this EIP was introduced in (if any)."""
        return cls._fork

    @classmethod
    def from_id(cls, eip_id: int) -> Optional[Type["BaseEIP"]]:
        """Get an EIP implementation by its ID."""
        return BaseEIPMeta.get_eip(eip_id)

    @classmethod
    def all_eips(cls) -> Dict[int, Type["BaseEIP"]]:
        """Get all registered EIPs."""
        return BaseEIPMeta.get_all_eips()

    @classmethod
    def by_fork(cls, fork_name: str) -> List[Type["BaseEIP"]]:
        """Get all EIPs for a specific fork name."""
        return [eip for eip in cls.all_eips().values() if eip.fork_name() == fork_name]

    @classmethod
    def required_eips(cls) -> List[Type["BaseEIP"]]:
        """Return list of EIPs that must be enabled for this EIP to work."""
        return []

    @classmethod
    def incompatible_eips(cls) -> List[Type["BaseEIP"]]:
        """Return list of EIPs that cannot be enabled together with this EIP."""
        return []

    @classmethod
    def eip_precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """
        Return list of precompiles introduced by this EIP.
        Override in subclasses to return the actual precompiles.
        """
        return []

    @classmethod
    def eip_system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """
        Return list of system contracts introduced by this EIP.
        Override if your EIP adds new system contracts.
        """
        return []

    @classmethod
    def eip_tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """
        Return list of new transaction types introduced by this EIP.
        Override if your EIP adds new transaction types.
        """
        return []

    @classmethod
    def eip_gas_costs_override(
        cls,
        costs: GasCosts,
        block_number: int = 0,
        timestamp: int = 0,
    ) -> GasCosts:
        """
        Override or adjust gas costs for this EIP.
        Override in subclasses to mutate 'costs' for your EIP.
        """
        return costs


# EIP Type Alias
EIP = Type[BaseEIP]
