"""
Ethereum Specs EVM Transition tool frontend.

https://github.com/ethereum/execution-specs
"""

from pathlib import Path
from re import compile

from ethereum_test_forks import Fork

from .geth import GethTransitionTool


class ExecSpecsTransitionTool(GethTransitionTool):
    """
    Ethereum Specs `ethereum-spec-evm` Transition tool frontend wrapper class.

    The behavior of this tool is almost identical to go-ethereum's `evm t8n` command.
    """

    default_binary = Path("ethereum-spec-evm")
    detect_binary_pattern = compile(r"^ethereum-spec-evm\b")

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.
        Currently, ethereum-spec-evm provides no way to determine supported forks.
        """
        return True
