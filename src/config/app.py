"""
A module for managing application configurations.

Classes:
- AppConfig: Holds configurations for the application framework.
"""

from pathlib import Path

from pydantic import BaseModel


class AppConfig(BaseModel):
    """
    A class for accessing documentation-related configurations.
    """

    version: str = "3.0.0"
    """The version of the application framework."""

    ROOT_DIR: Path = Path(__file__).resolve().parents[2]
    """The root directory of the project."""
