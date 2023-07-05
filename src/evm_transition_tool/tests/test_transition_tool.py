"""
Test the transition tool and subclasses.
"""

import shutil
from pathlib import Path

import pytest

from evm_transition_tool import (
    EvmOneTransitionTool,
    GethTransitionTool,
    TransitionTool,
    UnknownTransitionToolError,
)


def test_default_tool():
    """
    Tests that the default t8n tool is set.
    """
    assert TransitionTool.default_tool is GethTransitionTool


def test_from_binary(monkeypatch):
    """
    Test that `from_binary` instantiates the correct subclass.
    """

    def mock_which(self):
        return "evm"

    # monkeypatch: the transition tools constructor raises an exception if the binary path does
    # not exist
    monkeypatch.setattr(shutil, "which", mock_which)

    assert isinstance(TransitionTool.from_binary_path(binary_path=None), GethTransitionTool)
    assert isinstance(TransitionTool.from_binary_path(binary_path=Path("evm")), GethTransitionTool)
    assert isinstance(
        TransitionTool.from_binary_path(binary_path=Path("evmone-t8n")), EvmOneTransitionTool
    )


def test_unknown_binary_path():
    """
    Test that `from_binary_path` raises `UnknownTransitionToolError` for unknown
    binary paths.
    """
    with pytest.raises(UnknownTransitionToolError):
        TransitionTool.from_binary_path(binary_path=Path("unknown_binary_path"))
