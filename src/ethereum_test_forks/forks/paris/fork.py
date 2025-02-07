"""Paris (Merge) fork definition."""

from typing import Optional

from .pre_merge import London


class Paris(
    London,
    transition_tool_name="Merge",
    blockchain_test_network_name="Paris",
):
    """Paris (Merge) fork."""

    @classmethod
    def header_prev_randao_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Prev Randao is required starting from Paris."""
        return True

    @classmethod
    def header_zero_difficulty_required(cls, block_number: int = 0, timestamp: int = 0) -> bool:
        """Zero difficulty is required starting from Paris."""
        return True

    @classmethod
    def get_reward(cls, block_number: int = 0, timestamp: int = 0) -> int:
        """Paris updates the reward to 0."""
        return 0

    @classmethod
    def engine_new_payload_version(
        cls, block_number: int = 0, timestamp: int = 0
    ) -> Optional[int]:
        """From Paris, payloads can be sent through the engine API."""
        return 1
