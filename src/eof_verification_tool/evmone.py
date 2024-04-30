"""
Evmone Transition tool interface.
"""

from pathlib import Path
from re import compile
from typing import Optional

from ethereum_test_forks import Fork

from .eof_tool import EOFTool


class EvmOneEOFTool(EOFTool):
    """
    Evmone `evmone-eofparse` EOF tool interface wrapper class.
    """

    default_binary = Path("evmone-eofparse")
    detect_binary_pattern = compile(r"^evmone-eofparse\b")
    eof_use_stream = True

    binary: Path
    cached_version: Optional[str] = None

    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        super().__init__(binary=binary)

    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool.
        Currently, evmone-eofparse provides no way to determine supported forks.
        """
        return True
