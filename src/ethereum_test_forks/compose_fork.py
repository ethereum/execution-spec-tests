"""A fork class and decorator that are used to create a fork with a set of EIPs."""

from typing import Any, Dict, List, Type

from ethereum_test_base_types import Address

from .base_eip import BaseEIP, BaseEIPMeta
from .base_fork import BaseFork, BaseForkMeta, Fork
from .gas_costs import GasCosts


class CompositeMeta(BaseForkMeta, BaseEIPMeta):
    """A metaclass that handles both Fork and EIP functionality."""

    def __new__(mcs, name: str, bases: tuple, namespace: Dict[str, Any], **kwargs) -> Any:
        """Create a new class with the combined metaclass functionality."""
        fork_kwargs = {
            "transition_tool_name": kwargs.pop("transition_tool_name", None),
            "blockchain_test_network_name": kwargs.pop("blockchain_test_network_name", None),
            "solc_name": kwargs.pop("solc_name", None),
            "ignore": kwargs.pop("ignore", False),
        }
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls._transition_tool_name = fork_kwargs["transition_tool_name"]
        cls._blockchain_test_network_name = fork_kwargs["blockchain_test_network_name"]
        cls._solc_name = fork_kwargs["solc_name"]
        cls._ignore = fork_kwargs["ignore"]
        return cls


class ComposeFork(BaseFork, metaclass=CompositeMeta):
    """
    A base class that automatically composes all EIPs found in the MRO (method resolution order).
    Any fork inheriting from this class will automatically merge the EIP deltas for precompiles,
    gas costs, etc.
    """

    @classmethod
    def all_eips(cls) -> List[Type[BaseEIP]]:
        """
        Return a list of all EIPs found in the MRO of the class.
        Skips the BaseFork, BaseEIP, and ComposeFork classes so only the EIPs are returned.
        """
        eips = []
        seen = set()
        for base in cls.__mro__:
            if base in seen:
                continue
            seen.add(base)
            if base is BaseFork or base is BaseEIP or base is ComposeFork:
                continue
            if issubclass(base, ComposeFork):
                continue
            if isinstance(base, type) and issubclass(base, BaseEIP):
                eips.append(base)
        return eips

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return the precompiles for the fork and all EIPs."""
        base_pre = super().precompiles(block_number, timestamp)
        for eip_cls in cls.all_eips():
            if hasattr(eip_cls, "eip_precompiles"):
                base_pre.extend(eip_cls.eip_precompiles())
        return base_pre

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return the system contracts for the fork and all EIPs."""
        base_sys = super().system_contracts(block_number, timestamp)
        for eip_cls in cls.all_eips():
            if hasattr(eip_cls, "eip_system_contracts"):
                base_sys.extend(eip_cls.eip_system_contracts())
        return base_sys

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """Return the transaction types for the fork and all EIPs."""
        base_types = super().tx_types(block_number, timestamp)
        for eip_cls in cls.all_eips():
            if hasattr(eip_cls, "eip_tx_types"):
                base_types.extend(eip_cls.eip_tx_types())
        return list(dict.fromkeys(base_types))

    @classmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """Return the gas costs for the fork and all EIPs."""
        costs = super().gas_costs(block_number, timestamp)
        for eip_cls in reversed(cls.all_eips()):
            if hasattr(eip_cls, "eip_gas_costs_override"):
                costs = eip_cls.eip_gas_costs_override(
                    costs, block_number=block_number, timestamp=timestamp
                )
        return costs


def compose_fork(*eips: Type[BaseEIP]) -> Type[Fork]:
    """
    Class decorator that dynamically creates a new class inheriting from, `ComposeFork` and the
    the original fork class and all given EIPs in order.
    """

    def decorator(original_fork_cls: Type[BaseFork]) -> Type[BaseFork]:
        original_bases = original_fork_cls.__bases__
        new_bases = original_bases + (ComposeFork,) + eips
        new_class = CompositeMeta(
            original_fork_cls.__name__, new_bases, dict(original_fork_cls.__dict__)
        )
        new_class.__module__ = original_fork_cls.__module__

        # Remove the original class from the registry so only the composite remains.
        from .base_fork import BaseForkMeta

        if original_fork_cls in BaseForkMeta._base_forks_registry:
            BaseForkMeta._base_forks_registry.remove(original_fork_cls)
        return new_class

    return decorator
