"""
Test spec debugging tools.
"""

from typing import List

from rich.console import Console
from rich.text import Text

from evm_transition_tool import EVMTransactionTrace, TraceableException

console = Console()


def print_traces(*, exception: Exception | None, traces: List[List[EVMTransactionTrace]] | None):
    """
    Print the traces from the transition tool for debugging.
    """
    if traces is None:
        console.print(
            Text("Traces not collected. Use `--traces` to see detailed execution information.")
        )
        return

    if exception is not None and isinstance(exception, TraceableException):
        console.print(dict(enumerate(exception.get_relevant_traces(traces), start=1)))
    else:
        console.print(traces)
