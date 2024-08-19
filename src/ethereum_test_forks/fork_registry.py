"""
Define a global registry for forks that can be used in the Ethereum test
framework.

This approach allows different chains to register their fork class 
definitions.
"""

from typing import Dict, Type
from .base_fork import BaseFork
from .helpers import get_forks

fork_registry: Dict[str, Dict[str, Type[BaseFork]]] = {}

fork_registry["ethereum-mainnet"] = {fork.name(): fork for fork in get_forks()}


def update_fork_registry(chain_name: str, forks: Dict[str, Type[BaseFork]]):
    """
    Updates the global fork registry with forks from a specific chain.
    If the chain already exists, it merges the new forks with the existing ones.
    """
    if chain_name in fork_registry:
        fork_registry[chain_name].update(forks)
    else:
        fork_registry[chain_name] = forks


def get_fork_registry() -> Dict[str, Dict[str, Type[BaseFork]]]:
    """
    Returns the current fork registry.
    """
    return fork_registry
