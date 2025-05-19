"""
A module for managing application configurations.

Classes:
- AppConfig: Holds configurations for the application framework.
"""

from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    """A class for accessing documentation-related configurations."""

    version: str = "v4.5.0 (Hradčany)"
    """The version of the application framework."""

    DEFAULT_LOGS_DIR: Path = Path(__file__).resolve().parent.parent.parent / "logs"
    """The default directory where log files are stored."""

    DEFAULT_EVM_LOGS_DIR: Path = DEFAULT_LOGS_DIR / "evm"
    """The default directory where EVM log files are stored."""

    ROOT_DIR: Path = Path(__file__).resolve().parents[2]
    """The root directory of the project."""
