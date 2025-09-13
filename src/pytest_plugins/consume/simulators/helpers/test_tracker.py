"""Test tracking utilities for pre-allocation group lifecycle management."""

import logging
from dataclasses import dataclass, field
from typing import Dict, Set

import pytest

logger = logging.getLogger(__name__)


@dataclass
class PreAllocGroupTestTracker:
    """
    Tracks test execution progress per test group.

    This class enables automatic client cleanup by monitoring when all tests
    in a group have completed execution. Groups can be either pre-allocation
    groups (sequential execution) or xdist subgroups (parallel execution).
    """

    group_test_counts: Dict[str, int] = field(default_factory=dict)
    """Total number of tests per group (group_identifier -> count)."""

    group_completed_tests: Dict[str, Set[str]] = field(default_factory=dict)
    """Completed test IDs per group (group_identifier -> {test_ids})."""

    def set_group_test_count(self, group_identifier: str, total_tests: int) -> None:
        """
        Set the total number of tests for a group.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)
            total_tests: Total number of tests in this group

        """
        if group_identifier in self.group_test_counts:
            existing_count = self.group_test_counts[group_identifier]
            if existing_count != total_tests:
                logger.warning(
                    f"Group {group_identifier} test count mismatch: "
                    f"existing={existing_count}, new={total_tests}"
                )

        self.group_test_counts[group_identifier] = total_tests
        if group_identifier not in self.group_completed_tests:
            self.group_completed_tests[group_identifier] = set()

        logger.debug(f"Set test count for group {group_identifier}: {total_tests}")

    def mark_test_completed(self, group_identifier: str, test_id: str) -> bool:
        """
        Mark a test as completed for the given group.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)
            test_id: The unique test identifier

        Returns:
            True if all tests in the group are now complete

        """
        if group_identifier not in self.group_completed_tests:
            self.group_completed_tests[group_identifier] = set()

        # Avoid double-counting the same test
        if test_id in self.group_completed_tests[group_identifier]:
            logger.debug(
                f"Test {test_id} already marked as completed for group {group_identifier}"
            )
            return self.is_group_complete(group_identifier)

        self.group_completed_tests[group_identifier].add(test_id)
        completed_count = len(self.group_completed_tests[group_identifier])
        total_count = self.group_test_counts.get(group_identifier, 0)

        logger.debug(
            f"Test {test_id} completed for group {group_identifier} "
            f"({completed_count}/{total_count})"
        )

        is_complete = self.is_group_complete(group_identifier)
        if is_complete:
            logger.info(
                f"All tests completed for group {group_identifier} "
                f"({completed_count}/{total_count}) - ready for client cleanup"
            )

        return is_complete

    def is_group_complete(self, group_identifier: str) -> bool:
        """
        Check if all tests in a group have completed.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)

        Returns:
            True if all tests in the group are complete

        """
        if group_identifier not in self.group_test_counts:
            logger.warning(f"No test count found for group {group_identifier}")
            return False

        total_count = self.group_test_counts[group_identifier]
        completed_count = len(self.group_completed_tests.get(group_identifier, set()))

        return completed_count >= total_count

    def get_completion_status(self, group_identifier: str) -> tuple[int, int]:
        """
        Get completion status for a group.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)

        Returns:
            Tuple of (completed_count, total_count)

        """
        total_count = self.group_test_counts.get(group_identifier, 0)
        completed_count = len(self.group_completed_tests.get(group_identifier, set()))
        return completed_count, total_count

    def get_all_completion_status(self) -> Dict[str, tuple[int, int]]:
        """
        Get completion status for all tracked groups.

        Returns:
            Dict mapping group_identifier to (completed_count, total_count)

        """
        return {
            group_identifier: self.get_completion_status(group_identifier)
            for group_identifier in self.group_test_counts
        }

    def reset_group(self, group_identifier: str) -> None:
        """
        Reset tracking data for a specific group.

        Args:
            group_identifier: The group identifier to reset

        """
        if group_identifier in self.group_test_counts:
            del self.group_test_counts[group_identifier]
        if group_identifier in self.group_completed_tests:
            del self.group_completed_tests[group_identifier]
        logger.debug(f"Reset tracking data for group {group_identifier}")

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
        for group_identifier, count in group_counts.items():
            tracker.set_group_test_count(group_identifier, count)
        logger.info(f"Loaded test counts for {len(group_counts)} groups")

    logger.info("Pre-allocation group test tracker initialized")
    return tracker


@dataclass
class FCUFrequencyTracker:
    """
    Tracks forkchoice update frequency per group.

    This class enables controlling how often forkchoice updates are performed
    during test execution on a per-group basis (supporting both pre-allocation
    groups and xdist subgroups).
    """

    fcu_frequency: int
    """Frequency of FCU operations (0=disabled, 1=every test, N=every Nth test)."""

    group_test_counters: Dict[str, int] = field(default_factory=dict)
    """Test counters per group (group_identifier -> count)."""

    def should_perform_fcu(self, group_identifier: str) -> bool:
        """
        Check if forkchoice update should be performed for this test.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)

        Returns:
            True if FCU should be performed for this test

        """
        if self.fcu_frequency == 0:
            logger.debug(f"FCU disabled for group {group_identifier} (frequency=0)")
            return False

        current_count = self.group_test_counters.get(group_identifier, 0)
        should_perform = (current_count % self.fcu_frequency) == 0

        logger.debug(
            f"FCU decision for group {group_identifier}: "
            f"perform={should_perform} (test_count={current_count}, "
            f"frequency={self.fcu_frequency})"
        )

        return should_perform

    def increment_test_count(self, group_identifier: str) -> None:
        """
        Increment test counter for group.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)

        """
        current_count = self.group_test_counters.get(group_identifier, 0)
        new_count = current_count + 1
        self.group_test_counters[group_identifier] = new_count

        logger.debug(
            f"Incremented test count for group {group_identifier}: {current_count} -> {new_count}"
        )

    def get_test_count(self, group_identifier: str) -> int:
        """
        Get current test count for group.

        Args:
            group_identifier: The group identifier (pre_hash or xdist group name)

        Returns:
            Current test count for the group

        """
        return self.group_test_counters.get(group_identifier, 0)

    def get_all_test_counts(self) -> Dict[str, int]:
        """
        Get test counts for all tracked groups.

        Returns:
            Dict mapping group_identifier to test count

        """
        return dict(self.group_test_counters)

    def reset_group(self, group_identifier: str) -> None:
        """
        Reset test counter for a specific group.

        Args:
            group_identifier: The group identifier to reset

        """
        if group_identifier in self.group_test_counters:
            del self.group_test_counters[group_identifier]
        logger.debug(f"Reset test counter for group {group_identifier}")

    def reset_all(self) -> None:
        """Reset all test counters."""
        self.group_test_counters.clear()
        logger.debug("Reset all FCU frequency test counters")
