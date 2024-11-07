"""
Abstract base class for `evm statetest` subcommands.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type

from ethereum_test_exceptions import ExceptionMapper

from .ethereum_cli import EthereumCLI


class Statetest(EthereumCLI):
    """
    Abstract base class for `evm statetest` subcommands.
    """

    registered_tools: List[Type["Statetest"]] = []
    default_tool: Optional[Type["Statetest"]] = None

    blocktest_subcommand: Optional[str] = "statetest"

    traces: List[List[List[Dict]]] | None = None

    @abstractmethod
    def __init__(
        self,
        *,
        exception_mapper: Optional[ExceptionMapper] = None,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        """
        Abstract initialization method that all subclasses must implement.
        """
        self.exception_mapper = exception_mapper
        super().__init__(binary=binary)
        self.trace = trace
