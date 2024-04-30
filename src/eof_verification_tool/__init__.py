"""
Library of Python wrappers for the different implementations of EOF tools.
"""

from .eof_tool import EOFTool, EOFToolNotFoundInPath, UnknownEOFTool
from .evmone import EvmOneEOFTool

EOFTool.set_default_tool(EvmOneEOFTool)

__all__ = (
    "EvmOneEOFTool",
    "EOFTool",
    "EOFToolNotFoundInPath",
    "UnknownEOFTool",
)
