"""
Yul frontend
"""

from .code import Code

import subprocess
from pathlib import Path

SOLC: Path = Path("solc")
SOLC_ARGS = [
                SOLC,
                "--assemble",
                "-",
            ]

class Yul(Code):
    """
    Yul compiler.
    Compiles Yul source code into bytecode.
    """
    source : str
    compiled : bytes

    def __init__(self, source: str) -> "Yul":
        self.source = source
        self.compiled = None
    
    def assemble(self) -> bytes:
        """
        Assembles using `solc --assemble`.
        """
        if not self.compiled:

            result = subprocess.run(
                SOLC_ARGS,
                input=str.encode(self.source),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if result.returncode != 0:
                raise Exception("failed to compile yul source")

            lines = result.stdout.decode().split('\n')

            hex_str = lines[lines.index('Binary representation:') + 1]

            self.compiled = bytes.fromhex(hex_str)
        return self.compiled
        