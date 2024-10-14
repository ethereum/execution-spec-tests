"""
Base class for interacting with Ethereum CLIs.
"""

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from itertools import groupby
from pathlib import Path
from re import Pattern
from typing import Any, List, Optional, Type


class UnknownCLI(Exception):
    """Exception raised if an unknown t8n is encountered"""

    pass


class CLINotFoundInPath(Exception):
    """Exception raised if the specified t8n tool is not found in the path"""

    def __init__(self, message="The transition tool was not found in the path", binary=None):
        if binary:
            message = f"{message} ({binary})"
        super().__init__(message)


class EthereumCLI(ABC):
    """
    Abstract base class to help create an Ethereum CLI.
    """

    registered_tools: List[Type[Any]] = []
    default_tool: Optional[Type[Any]] = None
    default_binary: Path
    detect_binary_pattern: Pattern
    version_flag: str = "-v"
    cached_version: Optional[str] = None

    # Abstract methods that each tool must implement

    @abstractmethod
    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
        trace: bool = False,
    ):
        """
        Abstract initialization method that all subclasses must implement.
        """
        if binary is None:
            binary = self.default_binary
        else:
            # improve behavior of which by resolving the path: ~/relative paths don't work
            resolved_path = Path(os.path.expanduser(binary)).resolve()
            if resolved_path.exists():
                binary = resolved_path
        binary = shutil.which(binary)  # type: ignore
        if not binary:
            raise CLINotFoundInPath(binary=binary)
        self.binary = Path(binary)
        self.trace = trace

    @classmethod
    def register_tool(cls, tool_subclass: Type[Any]):
        """
        Registers a given subclass as tool option.
        """
        cls.registered_tools.append(tool_subclass)  # raise NotImplementedError

    @classmethod
    def set_default_tool(cls, tool_subclass: Type[Any]):
        """
        Registers the default tool subclass.
        """
        cls.default_tool = tool_subclass

    @classmethod
    def from_binary_path(cls, *, binary_path: Optional[Path], **kwargs) -> Any:
        """
        Instantiates the appropriate TransitionTool subclass derived from the
        tool's binary path.
        """
        assert cls.default_tool is not None, "default transition tool was never set"

        if binary_path is None:
            return cls.default_tool(binary=binary_path, **kwargs)

        resolved_path = Path(os.path.expanduser(binary_path)).resolve()
        if resolved_path.exists():
            binary_path = resolved_path
        binary = shutil.which(binary_path)  # type: ignore

        if not binary:
            raise CLINotFoundInPath(binary=binary)

        binary = Path(binary)

        # Group the tools by version flag, so we only have to call the tool once for all the
        # classes that share the same version flag
        for version_flag, subclasses in groupby(
            cls.registered_tools, key=lambda x: x.version_flag
        ):
            try:
                result = subprocess.run(
                    [binary, version_flag], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if result.returncode != 0:
                    raise Exception(f"Non-zero return code: {result.returncode}")

                if result.stderr:
                    raise Exception(f"Tool wrote to stderr: {result.stderr.decode()}")

                binary_output = ""
                if result.stdout:
                    binary_output = result.stdout.decode().strip()
            except Exception:
                # If the tool doesn't support the version flag,
                # we'll get an non-zero exit code.
                continue
            for subclass in subclasses:
                if subclass.detect_binary(binary_output):
                    return subclass(binary=binary, **kwargs)

        raise UnknownCLI(f"Unknown CLI: {binary_path}")

    @classmethod
    def detect_binary(cls, binary_output: str) -> bool:
        """
        Returns True if the binary matches the tool
        """
        assert cls.detect_binary_pattern is not None

        return cls.detect_binary_pattern.match(binary_output) is not None

    def version(self) -> str:
        """
        Return name and version of tool used to state transition
        """
        if self.cached_version is None:
            result = subprocess.run(
                [str(self.binary), self.version_flag],
                stdout=subprocess.PIPE,
            )

            if result.returncode != 0:
                raise Exception("failed to evaluate: " + result.stderr.decode())

            self.cached_version = result.stdout.decode().strip()

        return self.cached_version
