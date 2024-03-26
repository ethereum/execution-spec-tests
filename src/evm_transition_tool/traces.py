"""
Transition tool abstract traces.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Generator, List, TextIO, Type

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

HexNumber = Annotated[int, BeforeValidator(lambda x: int(x, 16))]
Bytes = Annotated[bytes, BeforeValidator(lambda x: bytes.fromhex(x[2:]))]


class TraceModel(BaseModel):
    """
    Base class all trace line types.
    """

    _mark_info: str = ""

    model_config = ConfigDict(alias_generator=to_camel)

    def match_stack(self, other: List[HexNumber | None]) -> bool:
        """
        Check if the trace line matches the given stack.

        The comparison happens in reverse order, so the last element of the
        stack is compared to the first element of the other stack.

        If an element of the other stack is None, it is considered a wildcard
        and will mark any value.
        """
        stack = getattr(self, "stack", [])
        assert isinstance(stack, list)
        if len(other) > len(stack):
            return False

        for i, value in enumerate(other):
            if value is not None and value != stack[-(i + 1)]:
                return False

        return True

    def mark(self, description: str, **kwargs):
        """
        Check if the trace call frame enter matches the given values.
        """
        for key, value in kwargs.items():
            if key == "stack":
                if not self.match_stack(value):
                    return
            elif callable(value):
                if not value(getattr(self, key)):
                    return
            elif value != getattr(self, key):
                return
        self._mark_info = description


class EVMCallFrameEnter(TraceModel):
    """
    Represents a single line of an EVM call entering a new frame.
    """

    # op: int | None = Field(None)
    op_name: str | None = Field(None, alias="type")
    from_address: str = Field(..., alias="from")
    to_address: str = Field(..., alias="to")
    input: Bytes | None = Field(None)
    gas: HexNumber
    value: HexNumber


class EVMCallFrameExit(TraceModel):
    """
    Represents a single line of an EVM call entering a new frame.
    """

    from_address: str | None = Field(None, alias="from")
    output: Bytes | None = Field(None)
    gas_used: HexNumber
    error: str | None = Field(None)


class EVMTraceLine(TraceModel):
    """
    Represents a single line of an EVM trace.
    """

    pc: int
    op: int
    op_name: str
    gas: HexNumber
    gas_cost: HexNumber
    mem_size: int
    stack: List[HexNumber]
    depth: int
    refund: int
    context_address: str | None = Field(None)


class EVMTransactionTrace(BaseModel):
    """
    Represents the trace of an EVM transaction.
    """

    trace: List[EVMCallFrameEnter | EVMTraceLine | EVMCallFrameExit]
    transaction_hash: str

    def model_post_init(self: "EVMTransactionTrace", __context: Any):
        """
        Fill the context address of the trace lines.
        """
        super().model_post_init(__context)

        context_stack: List[str] = []
        for line in self.trace:
            if isinstance(line, EVMCallFrameEnter):
                context_stack.append(line.to_address)
            elif isinstance(line, EVMCallFrameExit):
                line.from_address = context_stack.pop()
            elif isinstance(line, EVMTraceLine):
                line.context_address = context_stack[-1] if context_stack else None

    def get_trace_line_with_context(
        self, *, line_number: int, previous_lines: int = 0
    ) -> List[EVMCallFrameEnter | EVMTraceLine | EVMCallFrameExit]:
        """
        Get the trace line plus context.
        """
        if not self.trace:
            return []
        return self.trace[max(0, line_number - previous_lines) : line_number + 1]

    def get_trace_line_with_context_as_str(
        self, *, line_number: int, previous_lines: int = 0
    ) -> List[str]:
        """
        Get the trace line as string plus context of previous lines if required.
        """
        return [
            f"  {dict(trace)}"
            for trace in self.get_trace_line_with_context(
                line_number=line_number, previous_lines=previous_lines
            )
        ]

    @classmethod
    def from_file(cls, *, file_handler: TextIO, transaction_hash: str):
        """
        Create an EVMTransactionTrace from a file handler.
        """
        return cls(
            trace=[json.loads(line.strip()) for line in file_handler],
            transaction_hash=transaction_hash,
        )


class TraceMarkerDescriptor:
    """
    Class used to describe a marker for traces.
    """

    trace_type: Type[TraceModel]
    description: str
    kwargs: Dict[str, Any] = {}

    def __init__(
        self,
        *,
        trace_type: Type[TraceModel],
        description: str,
        **kwargs,
    ):
        self.trace_type = trace_type
        self.description = description
        self.kwargs = kwargs

    def mark_traces(self, traces: List[List[EVMTransactionTrace]] | None):
        """
        Mark the traces that are relevant to the exception.
        """
        if not traces:
            return

        for execution_trace in traces:
            for tx_trace in execution_trace:
                for trace in tx_trace.trace:
                    if isinstance(trace, self.trace_type):
                        trace.mark(description=self.description, **self.kwargs)


class RelevantTraceContext(BaseModel):
    """
    Context for a trace line.
    """

    execution_index: int
    transaction_index: int
    transaction_hash: str
    traces: List[EVMCallFrameEnter | EVMTraceLine | EVMCallFrameExit]
    description: str


class TraceableException(Exception, ABC):
    """
    Exception that can use a trace to provide more information.
    """

    @property
    @abstractmethod
    def markers(self) -> Generator[TraceMarkerDescriptor, None, None]:
        """
        Return the description of the exception.
        """
        raise NotImplementedError

    def get_relevant_traces(
        self,
        traces: List[List[EVMTransactionTrace]] | None,
        context_previous_lines: int = 2,
    ) -> Generator[RelevantTraceContext, None, None]:
        """
        Get the relevant traces for the exception.
        """
        if not traces:
            return

        for marker in self.markers:
            marker.mark_traces(traces)

        for execution_index, execution_trace in enumerate(traces):
            for tx_index, tx_trace in enumerate(execution_trace):
                for line_number, trace in enumerate(tx_trace.trace):
                    if trace._mark_info:
                        yield RelevantTraceContext(
                            execution_index=execution_index,
                            transaction_index=tx_index,
                            transaction_hash=tx_trace.transaction_hash,
                            traces=tx_trace.get_trace_line_with_context(
                                line_number=line_number, previous_lines=context_previous_lines
                            ),
                            description=trace._mark_info,
                        )
