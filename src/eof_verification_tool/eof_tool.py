"""
EOF verification tool abstract class.
"""

import json
import os
import shutil
import subprocess
from abc import abstractmethod
from itertools import groupby
from pathlib import Path
from re import Pattern
from typing import Any, Dict, List, Optional, Type

from ethereum_test_forks import Fork


class UnknownEOFTool(Exception):
    """Exception raised if an unknown eof is encountered"""

    pass


class EOFToolNotFoundInPath(Exception):
    """Exception raised if the specified eof tool is not found in the path"""

    def __init__(self, message="The eof tool was not found in the path", binary=None):
        if binary:
            message = f"{message} ({binary})"
        super().__init__(message)


class EOFTool:
    """
    EOF tool abstract base class which should be inherited by all eof tool
    implementations.
    """

    registered_tools: List[Type["EOFTool"]] = []
    default_tool: Optional[Type["EOFTool"]] = None
    default_binary: Path
    detect_binary_pattern: Pattern
    version_flag: str = "-v"
    eof_subcommand: Optional[str] = None
    cached_version: Optional[str] = None
    eof_use_stream: bool = True

    # Abstract methods that each tool must implement

    @abstractmethod
    def __init__(
        self,
        *,
        binary: Optional[Path] = None,
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
            raise EOFToolNotFoundInPath(binary=binary)
        self.binary = Path(binary)

    def __init_subclass__(cls):
        """
        Registers all subclasses of EOFTool as possible tools.
        """
        EOFTool.register_tool(cls)

    @classmethod
    def register_tool(cls, tool_subclass: Type["EOFTool"]):
        """
        Registers a given subclass as tool option.
        """
        cls.registered_tools.append(tool_subclass)

    @classmethod
    def set_default_tool(cls, tool_subclass: Type["EOFTool"]):
        """
        Registers the default tool subclass.
        """
        cls.default_tool = tool_subclass

    @classmethod
    def from_binary_path(cls, *, binary_path: Optional[Path], **kwargs) -> "EOFTool":
        """
        Instantiates the appropriate EOFTool subclass derived from the
        tool's binary path.
        """
        assert cls.default_tool is not None, "default eof tool was never set"

        if binary_path is None:
            return cls.default_tool(binary=binary_path, **kwargs)

        resolved_path = Path(os.path.expanduser(binary_path)).resolve()
        if resolved_path.exists():
            binary_path = resolved_path
        binary = shutil.which(binary_path)  # type: ignore

        if not binary:
            raise EOFToolNotFoundInPath(binary=binary)

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

        raise UnknownEOFTool(f"Unknown eof tool binary: {binary_path}")

    @classmethod
    def detect_binary(cls, binary_output: str) -> bool:
        """
        Returns True if the binary matches the tool
        """
        assert cls.detect_binary_pattern is not None

        return cls.detect_binary_pattern.match(binary_output) is not None

    def version(self) -> str:
        """
        Return name and version of tool used to eof verification
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

    @abstractmethod
    def is_fork_supported(self, fork: Fork) -> bool:
        """
        Returns True if the fork is supported by the tool
        """
        pass

    def shutdown(self):
        """
        Perform any cleanup tasks related to the tested tool.
        """
        pass

    def _evaluate_filesystem(
        self,
        *,
        eof_code: str,
    ) -> Dict[str, Any]:
        """
        Executes eof tool using the filesystem for its inputs and outputs.
        """
        # Construct args for eof verification binary
        args = [
            str(self.binary),
            "--state.fork",
            t8n_data.fork_name,
        ]

        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception("failed to evaluate: " + result.stderr.decode())

        return result.stderr

    def _evaluate_stream(
        self,
        *,
        eof_code: str,
    ) -> Dict[str, Any]:
        """
        Executes eof tool using stdin and stdout for its inputs and outputs.
        """

        args = ""
        stdin = {
            "alloc": eof_code,
        }

        result = subprocess.run(
            args,
            input=str.encode(json.dumps(stdin)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception("failed to evaluate: " + result.stderr.decode())

        output = json.loads(result.stdout)

        return output

    def evaluate(
        self,
        *,
        eof_code: str,
    ) -> Dict[str, Any]:
        """
        Executes the relevant evaluate method as required by the `eof` tool.

        If a client's `eof` tool varies from the default behavior, this method
        can be overridden.
        """
        if self.eof_use_stream:
            return self._evaluate_stream(eof_code=eof_code)
        else:
            return self._evaluate_filesystem(eof_code=eof_code)
