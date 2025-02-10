"""A fork class and decorator that are used to create a fork with a set of EIPs."""

from typing import List, Type

from ethereum_test_base_types import Address

from .base_eip import EIP, BaseEIP, BaseEIPMeta
from .base_fork import BaseFork, BaseForkMeta, Fork
from .gas_costs import GasCosts


class CompositeMeta(BaseForkMeta, BaseEIPMeta):
    """A metaclass that combines BaseForkMeta and BaseEIPMeta."""

    pass


class ComposeFork(BaseFork, metaclass=CompositeMeta):
    """
    A base class that automatically composes all EIPs found in the MRO (method resolution order).
    Any fork inheriting from this class will automatically merge the EIP deltas for precompiles,
    gas costs, etc.
    """

    @classmethod
    def all_eips(cls) -> List[Type[BaseEIP]]:
        """Return a list of all EIPs found in the MRO of the class."""
        eips = []
        for base in cls.__mro__:
            if base is BaseFork:
                break
            if isinstance(base, type) and issubclass(base, BaseEIP) and base is not BaseEIP:
                eips.append(base)
        return eips

    @classmethod
    def precompiles(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return the precompiles for the fork and all EIPs."""
        base_pre = super().precompiles(block_number, timestamp)
        for eip_cls in cls.all_eips():
            base_pre.extend(eip_cls.eip_precompiles())
        return base_pre

    @classmethod
    def system_contracts(cls, block_number: int = 0, timestamp: int = 0) -> List[Address]:
        """Return the system contracts for the fork and all EIPs."""
        base_sys = super().system_contracts(block_number, timestamp)
        for eip_cls in cls.all_eips():
            base_sys.extend(eip_cls.eip_system_contracts())
        return base_sys

    @classmethod
    def tx_types(cls, block_number: int = 0, timestamp: int = 0) -> List[int]:
        """Return the transaction types for the fork and all EIPs."""
        base_types = super().tx_types(block_number, timestamp)
        for eip_cls in cls.all_eips():
            base_types.extend(eip_cls.eip_tx_types())
        return list(dict.fromkeys(base_types))

    @classmethod
    def gas_costs(cls, block_number: int = 0, timestamp: int = 0) -> GasCosts:
        """Return the gas costs for the fork and all EIPs."""
        costs = super().gas_costs(block_number, timestamp)
        for eip_cls in reversed(cls.all_eips()):
            costs = eip_cls.eip_gas_costs_override(
                costs, block_number=block_number, timestamp=timestamp
            )
        return costs


def compose_fork(*eips: Type[EIP]) -> Type[Fork]:
    """
    Class decorator that dynamically creates a new class inheriting from, `ComposeFork` and the
    the original fork class and all given EIPs in order.
    """

    def decorator(original_fork_cls: Type[BaseFork]) -> Type[BaseFork]:
        """Return the decorator that creates a new class."""
        original_bases = original_fork_cls.__bases__
        new_bases = (ComposeFork,) + original_bases + eips
        new_class = CompositeMeta(
            original_fork_cls.__name__,
            new_bases,
            dict(original_fork_cls.__dict__),
        )
        new_class.__module__ = original_fork_cls.__module__
        return new_class

    return decorator
