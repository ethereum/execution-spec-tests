"""
Transition tool abstract traces.
"""

import json
from typing import List, TextIO

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

HexNumber = Annotated[int, BeforeValidator(lambda x: int(x, 16))]


class EVMCallFrameLine(BaseModel):
    """
    Represents a single line of an EVM call entering a new frame.
    """

    opcode: int | None = Field(None, alias="op")
    opcode_name: str | None = Field(None, alias="opName")
    from_address: str = Field(..., alias="from")
    to_address: str = Field(..., alias="to")
    input: bytes | None = Field(None)
    gas: HexNumber = Field(..., alias="gas")
    value: HexNumber


class EVMTraceLine(BaseModel):
    """
    Represents a single line of an EVM trace.
    """

    pc: int
    opcode: int = Field(..., alias="op")
    opcode_name: str = Field(..., alias="opName")
    gas_left: HexNumber = Field(..., alias="gas")
    gas_cost: HexNumber = Field(..., alias="gasCost")
    memory_size: int = Field(..., alias="memSize")
    stack: List[HexNumber]
    depth: int
    refund: int
    context_address: str | None = Field(None)


class EVMTraceOutput(BaseModel):
    """
    Represents the output of an EVM trace.
    """

    output: str
    gas_used: HexNumber = Field(..., alias="gasUsed")


class EVMTransactionTrace(BaseModel):
    """
    Represents the trace of an EVM transaction.
    """

    trace: List[EVMCallFrameLine | EVMTraceLine]
    output: EVMTraceOutput
    transaction_hash: str

    def fill_context(self):
        """
        Fill the context address of the trace lines.
        """
        context_stack = []
        previous_depth = 0
        last_line_call_frame = False
        for line in self.trace:
            if isinstance(line, EVMCallFrameLine):
                context_stack.append(line.to_address)
                last_line_call_frame = True
            elif isinstance(line, EVMTraceLine):
                if line.depth < previous_depth or (
                    line.depth == previous_depth and last_line_call_frame
                ):
                    context_stack.pop()

                line.context_address = context_stack[-1] if context_stack else None
                last_line_call_frame = False

    def call_frames(self):
        """
        Return the call frames of the transaction.
        """
        return [line for line in self.trace if isinstance(line, EVMCallFrameLine)]

    def trace_lines(self):
        """
        Return the trace lines of the transaction.
        """
        return [line for line in self.trace if isinstance(line, EVMTraceLine)]

    @classmethod
    def from_file(cls, *, file_handler: TextIO, transaction_hash: str):
        """
        Create an EVMTransactionTrace from a file handler.
        """
        trace = [json.loads(line) for line in file_handler]
        instance = cls(
            trace=trace[:-1],
            output=trace[-1],
            transaction_hash=transaction_hash,
        )
        instance.fill_context()
        return instance
