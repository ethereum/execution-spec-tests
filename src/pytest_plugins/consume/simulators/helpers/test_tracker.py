"""Test tracking utilities for pre-allocation group lifecycle management."""

import logging
from dataclasses import dataclass, field
from typing import Dict, Set

import pytest

logger = logging.getLogger(__name__)


@dataclass
class PreAllocGroupTestTracker:
    """
    Tracks test execution progress per pre-allocation group.

    This class enables automatic client cleanup by monitoring when all tests
    in a pre-allocation group have completed execution.
    """

    group_test_counts: Dict[str, int] = field(default_factory=dict)
    """Total number of tests per pre-allocation group (pre_hash -> count)."""

    group_completed_tests: Dict[str, Set[str]] = field(default_factory=dict)
    """Completed test IDs per pre-allocation group (pre_hash -> {test_ids})."""

    def set_group_test_count(self, pre_hash: str, total_tests: int) -> None:
        """
        Set the total number of tests for a pre-allocation group.

        Args:
            pre_hash: The pre-allocation group hash
            total_tests: Total number of tests in this group

        """
        if pre_hash in self.group_test_counts:
            existing_count = self.group_test_counts[pre_hash]
            if existing_count != total_tests:
                logger.warning(
                    f"Pre-allocation group {pre_hash} test count mismatch: "
                    f"existing={existing_count}, new={total_tests}"
                )

        self.group_test_counts[pre_hash] = total_tests
        if pre_hash not in self.group_completed_tests:
            self.group_completed_tests[pre_hash] = set()

        logger.debug(f"Set test count for pre-allocation group {pre_hash}: {total_tests}")

    def mark_test_completed(self, pre_hash: str, test_id: str) -> bool:
        """
        Mark a test as completed for the given pre-allocation group.

        Args:
            pre_hash: The pre-allocation group hash
            test_id: The unique test identifier

        Returns:
            True if all tests in the pre-allocation group are now complete

        """
        if pre_hash not in self.group_completed_tests:
            self.group_completed_tests[pre_hash] = set()

        # Avoid double-counting the same test
        if test_id in self.group_completed_tests[pre_hash]:
            logger.debug(f"Test {test_id} already marked as completed for group {pre_hash}")
            return self.is_group_complete(pre_hash)

        self.group_completed_tests[pre_hash].add(test_id)
        completed_count = len(self.group_completed_tests[pre_hash])
        total_count = self.group_test_counts.get(pre_hash, 0)

        logger.debug(
            f"Test {test_id} completed for pre-allocation group {pre_hash} "
            f"({completed_count}/{total_count})"
        )

        is_complete = self.is_group_complete(pre_hash)
        if is_complete:
            logger.info(
                f"All tests completed for pre-allocation group {pre_hash} "
                f"({completed_count}/{total_count}) - ready for client cleanup"
            )

        return is_complete

    def is_group_complete(self, pre_hash: str) -> bool:
        """
        Check if all tests in a pre-allocation group have completed.

        Args:
            pre_hash: The pre-allocation group hash

        Returns:
            True if all tests in the group are complete

        """
        if pre_hash not in self.group_test_counts:
            logger.warning(f"No test count found for pre-allocation group {pre_hash}")
            return False

        total_count = self.group_test_counts[pre_hash]
        completed_count = len(self.group_completed_tests.get(pre_hash, set()))

        return completed_count >= total_count

    def get_completion_status(self, pre_hash: str) -> tuple[int, int]:
        """
        Get completion status for a pre-allocation group.

        Args:
            pre_hash: The pre-allocation group hash

        Returns:
            Tuple of (completed_count, total_count)

        """
        total_count = self.group_test_counts.get(pre_hash, 0)
        completed_count = len(self.group_completed_tests.get(pre_hash, set()))
        return completed_count, total_count

    def get_all_completion_status(self) -> Dict[str, tuple[int, int]]:
        """
        Get completion status for all tracked pre-allocation groups.

        Returns:
            Dict mapping pre_hash to (completed_count, total_count)

        """
        return {
            pre_hash: self.get_completion_status(pre_hash) for pre_hash in self.group_test_counts
        }

    def reset_group(self, pre_hash: str) -> None:
        """
        Reset tracking data for a specific pre-allocation group.

        Args:
            pre_hash: The pre-allocation group hash to reset

        """
        if pre_hash in self.group_test_counts:
            del self.group_test_counts[pre_hash]
        if pre_hash in self.group_completed_tests:
            del self.group_completed_tests[pre_hash]
        logger.debug(f"Reset tracking data for pre-allocation group {pre_hash}")

    def reset_all(self) -> None:
        """Reset all tracking data."""
        self.group_test_counts.clear()
        self.group_completed_tests.clear()
        logger.debug("Reset all test tracking data")


@pytest.fixture(scope="session")
def pre_alloc_group_test_tracker(request) -> PreAllocGroupTestTracker:
    """
    Session-scoped test tracker for pre-allocation group lifecycle management.

    This fixture provides a centralized way to track test completion across
    all pre-allocation groups during a pytest session.
    """
    tracker = PreAllocGroupTestTracker()

    # Store tracker on session for access by collection hooks
    request.session._pre_alloc_group_test_tracker = tracker

    # Load pre-collected group counts if available
    if hasattr(request.session, "_pre_alloc_group_counts"):
        group_counts = request.session._pre_alloc_group_counts
        for pre_hash, count in group_counts.items():
            tracker.set_group_test_count(pre_hash, count)
        logger.info(f"Loaded test counts for {len(group_counts)} pre-allocation groups")

    logger.info("Pre-allocation group test tracker initialized")
    return tracker
