"""
Test timing class used to time tests.
"""

import time
from typing import Dict


class TimingData:
    """
    The times taken to perform the various steps of a test case (seconds).
    """

    start_time: float
    last_time: float
    timings: Dict[str, float] = {}

    def __init__(self):
        """
        Initialize the timing data.
        """
        self.start_time = self.last_time = time.perf_counter()

    @staticmethod
    def format_float(num: float | None, precision: int = 4) -> str | None:
        """
        Format a float to a specific precision in significant figures.
        """
        if num is None:
            return None
        return f"{num:.{precision}f}"

    def record(self, name: str) -> None:
        """
        Record the time taken since the last time recorded.
        """
        current_time = time.perf_counter()
        self.timings[name] = current_time - self.last_time
        self.last_time = current_time

    def finish(self) -> None:
        """
        Record the time taken since the last time recorded.
        """
        self.timings["total"] = time.perf_counter() - self.start_time

    def formatted(self, precision: int = 4) -> Dict[str, str | None]:
        """
        Return a new instance of the model with formatted float values.
        """
        data = {
            field: self.format_float(value, precision) for field, value in self.timings.items()
        }
        return data
