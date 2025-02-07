"""Base class for Ethereum Improvement Proposals (EIPs)."""

from abc import ABC, ABCMeta
from typing import Any, ClassVar, Dict, List, Optional, Protocol, Type

from ethereum_test_base_types import Address


class EIPAttribute(Protocol):
    """A protocol to get the attribute of an EIP at a given block number and timestamp."""

    def __call__(self, block_number: int = 0, timestamp: int = 0) -> Any:
        """Return value of the attribute at the given block number and timestamp."""
        pass


class BaseEIPMeta(ABCMeta):
    """Metaclass for BaseEIP."""

    _registry: Dict[int, Type["BaseEIP"]] = {}  # Use string for forward reference

    @property
    def eip_id(cls) -> int:
        """Extract EIP number from class name."""
        return int("".join(filter(str.isdigit, cls.__name__)))

    def __repr__(cls) -> str:
        """Print the EIP ID instead of the class name."""
        return f"EIP-{cls.eip_id}"

    @classmethod
    def get_eip(mcs, eip_id: int) -> Optional[Type["BaseEIP"]]:  # Use string for forward reference
        """Get an EIP implementation by its ID."""
        return mcs._registry.get(eip_id)

    @classmethod
    def get_all_eips(mcs) -> Dict[int, Type["BaseEIP"]]:  # Use string for forward reference
        """Get all registered EIPs."""
        return mcs._registry.copy()

    @classmethod
    def register_eip(mcs, eip_cls: Type["BaseEIP"]) -> None:  # Use string for forward reference
        """Register an EIP implementation."""
        mcs._registry[eip_cls.eip_id] = eip_cls


class BaseEIP(ABC, metaclass=BaseEIPMeta):
    """
    An abstract base class representing an Ethereum Improvement Proposal (EIP).
    Each EIP implementation should inherit from this class and implement
    the relevant methods for that specific EIP's functionality.
    """

    _fork: ClassVar[Optional[str]] = None

    def __init_subclass__(
        cls,
        *,
        fork: Optional[str] = None,
    ) -> None:
        """Initialize new EIP and register it in the registry."""
        cls._fork = fork
        BaseEIPMeta.register_eip(cls)

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return list of system contracts introduced by this EIP."""
        return []

    @classmethod
    def required_eips(cls) -> List[Type["BaseEIP"]]:  # Use string for forward reference
        """Return list of EIPs that must be enabled for this EIP to work."""
        return []

    @classmethod
    def incompatible_eips(cls) -> List[Type["BaseEIP"]]:  # Use string for forward reference
        """Return list of EIPs that cannot be enabled together with this EIP."""
        return []

    @classmethod
    def fork_name(cls) -> Optional[str]:
        """Return the name of the fork this EIP was introduced in."""
        return cls._fork

    @classmethod
    def from_id(cls, eip_id: int) -> Optional[Type["BaseEIP"]]:  # Use string for forward reference
        """Get an EIP implementation by its ID."""
        return BaseEIPMeta.get_eip(eip_id)

    @classmethod
    def all_eips(cls) -> Dict[int, Type["BaseEIP"]]:  # Use string for forward reference
        """Get all registered EIPs."""
        return BaseEIPMeta.get_all_eips()

    @classmethod
    def by_fork(cls, fork_name: str) -> List[Type["BaseEIP"]]:  # Use string for forward reference
        """Get all EIPs for a specific fork."""
        return [eip for eip in cls.all_eips().values() if eip.fork_name() == fork_name]

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return list of precompiles introduced by this EIP."""
        return []

    @classmethod
    def header_fields_required(cls, block_number: int = 0, timestamp: int = 0) -> List[str]:
        """Return list of header fields required by this EIP."""
        return []

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """Return list of transaction types introduced by this EIP."""
        return []


# Type alias for EIP references
EIP = Type[BaseEIP]
