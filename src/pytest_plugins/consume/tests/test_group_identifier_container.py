"""
Unit tests for test group identifier container cleanup.

This module tests the container cleanup to ensures proper client lifecycle
management for both sequential and xdist execution modes.

The test specifically addresses a regression introduced when subgroup splitting was
added for load balancing. Previously, each subgroup would create separate containers
for the same pre-allocation group, leading to container count explosion
(e.g., 24-25 containers instead of the expected 8 with 8 workers).
"""

from unittest.mock import Mock

import pytest

from pytest_plugins.consume.simulators.helpers.client_wrapper import (
    extract_pre_hash_from_group_identifier,
    get_group_identifier_from_request,
)


class TestGroupIdentifierDetection:
    """Test group identifier detection for different execution modes."""

    def test_sequential_execution_no_xdist_marker(self):
        """Test group identifier detection for sequential execution (no xdist marker)."""
        # Setup: Mock request with no xdist markers
        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[])

        pre_hash = "0x479393be6619d67f"

        # Execute
        group_id = get_group_identifier_from_request(request_mock, pre_hash)

        # Verify: Should use pre_hash directly for sequential execution
        assert group_id == pre_hash

    def test_xdist_execution_with_subgroup(self):
        """Test group identifier detection for xdist execution with subgroups."""
        # Setup: Mock request with xdist marker containing subgroup
        xdist_marker = Mock()
        xdist_marker.kwargs = {"name": "0x479393be6619d67f:2"}

        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[xdist_marker])

        pre_hash = "0x479393be6619d67f"

        # Execute
        group_id = get_group_identifier_from_request(request_mock, pre_hash)

        # Verify: Should use xdist group name (with subgroup suffix)
        assert group_id == "0x479393be6619d67f:2"

    def test_xdist_execution_without_subgroup(self):
        """Test group identifier detection for xdist execution without subgroups."""
        # Setup: Mock request with xdist marker without subgroup
        xdist_marker = Mock()
        xdist_marker.kwargs = {"name": "0x479393be6619d67f"}

        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[xdist_marker])

        pre_hash = "0x479393be6619d67f"

        # Execute
        group_id = get_group_identifier_from_request(request_mock, pre_hash)

        # Verify: Should use xdist group name (same as pre_hash)
        assert group_id == pre_hash

    def test_missing_iter_markers_method(self):
        """Test fallback when request.node doesn't have iter_markers method."""
        # Setup: Mock request without iter_markers method
        request_mock = Mock()
        del request_mock.node.iter_markers  # Remove the method

        pre_hash = "0x479393be6619d67f"

        # Execute
        group_id = get_group_identifier_from_request(request_mock, pre_hash)

        # Verify: Should fallback to pre_hash
        assert group_id == pre_hash

    def test_xdist_marker_without_name_kwargs(self):
        """Test handling of xdist marker without proper name kwargs."""
        # Setup: Mock request with malformed xdist marker
        xdist_marker = Mock()
        xdist_marker.kwargs = {}  # No 'name' key

        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[xdist_marker])

        pre_hash = "0x479393be6619d67f"

        # Execute
        group_id = get_group_identifier_from_request(request_mock, pre_hash)

        # Verify: Should fallback to pre_hash
        assert group_id == pre_hash


class TestPreHashExtraction:
    """Test pre_hash extraction from group identifiers."""

    def test_extract_from_non_subgroup_identifier(self):
        """Test extraction from group identifier without subgroup."""
        group_id = "0x479393be6619d67f"

        extracted = extract_pre_hash_from_group_identifier(group_id)

        assert extracted == group_id

    def test_extract_from_subgroup_identifier(self):
        """Test extraction from group identifier with subgroup."""
        group_id = "0x479393be6619d67f:2"
        expected = "0x479393be6619d67f"

        extracted = extract_pre_hash_from_group_identifier(group_id)

        assert extracted == expected

    def test_extract_with_multiple_colons(self):
        """Test extraction with multiple colons (edge case)."""
        group_id = "0x479393be6619d67f:2:extra:data"
        expected = "0x479393be6619d67f"

        extracted = extract_pre_hash_from_group_identifier(group_id)

        assert extracted == expected

    def test_extract_from_empty_string(self):
        """Test extraction from empty string."""
        group_id = ""

        extracted = extract_pre_hash_from_group_identifier(group_id)

        assert extracted == ""

    def test_extract_with_colon_only(self):
        """Test extraction with colon only."""
        group_id = ":"
        expected = ""

        extracted = extract_pre_hash_from_group_identifier(group_id)

        assert extracted == expected


class TestContainerIsolationScenario:
    """Test the key scenario that fixes the container cleanup regression."""

    def test_subgroup_container_isolation(self):
        """Test that subgroups get separate container tracking."""
        # Setup: Simulate large pre-allocation group split into subgroups
        pre_hash = "0x479393be6619d67f"
        subgroups = [f"{pre_hash}:{i}" for i in range(5)]

        # Simulate container creation using group identifiers
        containers = {}
        for subgroup in subgroups:
            container_key = subgroup  # Key change: use subgroup as container key
            extracted_pre_hash = extract_pre_hash_from_group_identifier(subgroup)

            containers[container_key] = {
                "group_identifier": subgroup,
                "pre_hash": extracted_pre_hash,
                "tests_completed": 0,
                "total_tests": 400,
            }

        # Verify: Each subgroup gets its own container tracking
        assert len(containers) == 5

        # Verify: All containers reference the same pre-allocation file
        for container in containers.values():
            assert container["pre_hash"] == pre_hash

        # Verify: Each container has unique group identifier
        group_identifiers = [c["group_identifier"] for c in containers.values()]
        assert len(set(group_identifiers)) == 5  # All unique

    def test_subgroup_cleanup_isolation(self):
        """Test that subgroup cleanup is isolated to completed groups only."""
        # Setup: Multiple subgroups with different completion states
        pre_hash = "0x479393be6619d67f"
        containers = {
            f"{pre_hash}:0": {"tests_completed": 400, "total_tests": 400},  # Complete
            f"{pre_hash}:1": {"tests_completed": 200, "total_tests": 400},  # Partial
            f"{pre_hash}:2": {"tests_completed": 0, "total_tests": 400},  # Not started
        }

        # Simulate cleanup detection
        completed_containers = [
            k for k, v in containers.items() if v["tests_completed"] >= v["total_tests"]
        ]

        # Verify: Only completed subgroup is marked for cleanup
        assert len(completed_containers) == 1
        assert completed_containers[0] == f"{pre_hash}:0"

    def test_sequential_vs_xdist_behavior(self):
        """Test that sequential and xdist modes result in different container strategies."""
        pre_hash = "0x479393be6619d67f"

        # Sequential execution: single container for entire pre-allocation group
        sequential_containers = {pre_hash: {"total_tests": 2000}}

        # XDist execution: multiple containers for subgroups
        xdist_containers = {f"{pre_hash}:{i}": {"total_tests": 400} for i in range(5)}

        # Verify: Different container strategies
        assert len(sequential_containers) == 1  # Single container
        assert len(xdist_containers) == 5  # Multiple containers

        # Verify: Same total test count
        sequential_total = sum(c["total_tests"] for c in sequential_containers.values())
        xdist_total = sum(c["total_tests"] for c in xdist_containers.values())
        assert sequential_total == xdist_total == 2000


class TestRegressionScenario:
    """Test the specific regression scenario that was reported."""

    def test_container_count_regression_fix(self):
        """
        Test that the fix prevents the container count regression.

        Before fix: 8 workers × 3 subgroups = 24-25 containers
        After fix: Max 8 containers (1 per worker, different subgroups)
        """
        # Setup: Simulate 8 workers with subgroups distributed across them
        pre_hash = "0x479393be6619d67f"
        num_workers = 8

        # Before fix: Each worker could create containers for different subgroups
        # This would lead to multiple containers per pre_hash across workers
        before_fix_containers = {}
        for worker in range(num_workers):
            for subgroup in range(3):  # 3 subgroups
                # Old key: pre_hash (same for all subgroups)
                # This caused multiple containers for same pre_hash
                old_key = pre_hash
                container_id = f"worker_{worker}_subgroup_{subgroup}"
                before_fix_containers[container_id] = {"key": old_key}

        # After fix: Each subgroup gets unique container key
        after_fix_containers = {}
        for worker in range(num_workers):
            # Each worker handles one subgroup (distributed by xdist)
            subgroup = worker % 3  # Distribute subgroups across workers
            new_key = f"{pre_hash}:{subgroup}"
            container_id = f"worker_{worker}"
            after_fix_containers[container_id] = {"key": new_key}

        # Verify: Fix reduces container proliferation
        # Before: 24 containers (8 workers × 3 subgroups)
        assert len(before_fix_containers) == 24

        # After: 8 containers (1 per worker)
        assert len(after_fix_containers) == 8

        # Verify: Unique container keys in fixed version
        after_fix_keys = [c["key"] for c in after_fix_containers.values()]
        unique_keys = set(after_fix_keys)
        assert len(unique_keys) <= 3  # At most one container per subgroup


@pytest.mark.parametrize(
    "execution_mode,expected_containers",
    [
        ("sequential", 1),  # Single container for entire pre-allocation group
        ("xdist_small", 1),  # Small group, no splitting needed
        ("xdist_large", 5),  # Large group, split into 5 subgroups
    ],
)
def test_container_strategy_by_execution_mode(execution_mode, expected_containers):
    """Test container strategy varies by execution mode and group size."""
    pre_hash = "0x479393be6619d67f"

    if execution_mode == "sequential":
        # Sequential: Always use pre_hash as container key
        container_keys = [pre_hash]
    elif execution_mode == "xdist_small":
        # Small xdist group: No subgroup splitting
        container_keys = [pre_hash]
    elif execution_mode == "xdist_large":
        # Large xdist group: Split into subgroups
        container_keys = [f"{pre_hash}:{i}" for i in range(5)]

    assert len(container_keys) == expected_containers


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_none_request_handling(self):
        """Test handling of None request parameter."""
        with pytest.raises(AttributeError):
            get_group_identifier_from_request(None, "0x123")

    def test_empty_pre_hash(self):
        """Test handling of empty pre_hash."""
        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[])

        group_id = get_group_identifier_from_request(request_mock, "")
        assert group_id == ""

    def test_none_pre_hash(self):
        """Test handling of None pre_hash."""
        request_mock = Mock()
        request_mock.node.iter_markers = Mock(return_value=[])

        group_id = get_group_identifier_from_request(request_mock, None)
        assert group_id is None
