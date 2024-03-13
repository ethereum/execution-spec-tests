"""
Transition tool abstract traces.
"""

import json
from typing import List, TextIO

from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

HexNumber = Annotated[int, BeforeValidator(lambda x: int(x, 16))]


class EVMCallFrameEnter(BaseModel):
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
    _marked: bool = False

    def mark(self, **kwargs) -> bool:
        """
        Check if the trace call frame enter matches the given values.
        """
        for key, value in kwargs.items():
            if callable(value):
                if not value(getattr(self, key)):
                    return False
            elif value != getattr(self, key):
                return False
        self._marked = True
        return True


class EVMCallFrameExit(BaseModel):
    """
    Represents a single line of an EVM call entering a new frame.
    """

    from_address: str = Field(..., alias="from")
    to_address: str = Field(..., alias="to")
    output: bytes | None = Field(None)
    gas_used: HexNumber = Field(..., alias="gasUsed")
    error: str | None = Field(None)
    _marked: bool = False

    def mark(self, **kwargs) -> bool:
        """
        Check if the trace call frame exit matches the given values.
        """
        for key, value in kwargs.items():
            if callable(value):
                if not value(getattr(self, key)):
                    return False
            elif value != getattr(self, key):
                return False
        self._marked = True
        return True


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
    _marked: bool = False

    def match_stack(self, other: List[HexNumber | None]) -> bool:
        """
        Check if the trace line matches the given stack.

        The comparison happens in reverse order, so the last element of the
        stack is compared to the first element of the other stack.

        If an element of the other stack is None, it is considered a wildcard
        and will mark any value.
        """
        if len(other) > len(self.stack):
            return False

        for i, value in enumerate(other):
            if value is not None and value != self.stack[-(i + 1)]:
                return False

        return True

    def mark(self, **kwargs) -> bool:
        """
        Check if the trace line matches the given values.
        """
        for key, value in kwargs.items():
            if key == "stack":
                if not self.match_stack(value):
                    return False
            elif callable(value):
                if not value(getattr(self, key)):
                    return False
            elif value != getattr(self, key):
                return False
        self._marked = True
        return True


class EVMTransactionTrace(BaseModel):
    """
    Represents the trace of an EVM transaction.
    """

    trace: List[EVMCallFrameEnter | EVMTraceLine | EVMCallFrameExit]
    transaction_hash: str

    def fill_context(self):
        """
        Fill the context address of the trace lines.
        """
        context_stack = []
        for line in self.trace:
            if isinstance(line, EVMCallFrameEnter):
                context_stack.append(line.to_address)
            elif isinstance(line, EVMCallFrameExit):
                context_stack.pop()
            elif isinstance(line, EVMTraceLine):
                line.context_address = context_stack[-1] if context_stack else None

    def call_frames(self):
        """
        Return the call frames of the transaction.
        """
        return [
            line
            for line in self.trace
            if isinstance(line, EVMCallFrameEnter) or isinstance(line, EVMCallFrameExit)
        ]

    def trace_lines(self):
        """
        Return the trace lines of the transaction.
        """
        return [line for line in self.trace if isinstance(line, EVMTraceLine)]

    def get_trace_line_with_context(
        self, *, line_number: int, previous_lines: int = 0
    ) -> List[str]:
        """
        Get the trace line as string plus context of previous lines if required.
        """
        if self.trace:
            return [
                f"  {dict(trace)}"
                for trace in self.trace[max(0, line_number - previous_lines) : line_number + 1]
            ]
        return []

    @classmethod
    def from_file(cls, *, file_handler: TextIO, transaction_hash: str):
        """
        Create an EVMTransactionTrace from a file handler.
        """
        instance = cls(
            trace=json.load(file_handler),
            transaction_hash=transaction_hash,
        )
        instance.fill_context()
        return instance
