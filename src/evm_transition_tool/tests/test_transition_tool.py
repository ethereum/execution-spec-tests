"""
Test the transition tool and subclasses.
"""

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

    def mock_exists(self):
        return True

    # monkeypatch the exists method: the transition tools constructor raises
    # an exception if the binary path does not exist
    monkeypatch.setattr(Path, "exists", mock_exists)

    assert isinstance(TransitionTool.from_binary_path(binary_path=None), GethTransitionTool)
    assert isinstance(TransitionTool.from_binary_path(binary_path="evm"), GethTransitionTool)
    assert isinstance(
        TransitionTool.from_binary_path(binary_path="evmone-t8n"), EvmOneTransitionTool
    )


def test_unknown_binary_path():
    """
    Test that `from_binary_path` raises `UnknownTransitionToolError` for unknown
    binary paths.
    """
    with pytest.raises(UnknownTransitionToolError):
        TransitionTool.from_binary_path(binary_path="unknown_binary_path")
