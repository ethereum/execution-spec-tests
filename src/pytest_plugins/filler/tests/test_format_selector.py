"""Unit tests for the FormatSelector class."""

from typing import Set

import pytest

from ethereum_test_fixtures import FixtureFillingPhase
from pytest_plugins.filler.filler import FormatSelector, PhaseManager


class MockFixtureFormat:
    """Mock fixture format for testing."""

    def __init__(self, format_phases: Set[FixtureFillingPhase]):
        """Initialize with format phases."""
        self.format_phases = format_phases


class MockLabeledFixtureFormat:
    """Mock labeled fixture format for testing."""

    def __init__(self, format_phases: Set[FixtureFillingPhase]):
        """Initialize with format phases."""
        self.format = MockFixtureFormat(format_phases)


class TestFormatSelector:
    """Test cases for FormatSelector class."""

    def test_init(self):
        """Test basic initialization."""
        phase_manager = PhaseManager(FixtureFillingPhase.FILL, set())
        format_selector = FormatSelector(phase_manager)
        assert format_selector.phase_manager is phase_manager

    def test_should_generate_pre_alloc_phase_with_pre_alloc_format(self):
        """Test pre-alloc phase with format that supports pre-alloc."""
        phase_manager = PhaseManager(FixtureFillingPhase.PRE_ALLOC_GENERATION, set())
        format_selector = FormatSelector(phase_manager)

        format_with_pre_alloc = MockFixtureFormat(
            {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL}
        )

        assert format_selector.should_generate(format_with_pre_alloc)

    def test_should_generate_pre_alloc_phase_without_pre_alloc_format(self):
        """Test pre-alloc phase with format that doesn't support pre-alloc."""
        phase_manager = PhaseManager(FixtureFillingPhase.PRE_ALLOC_GENERATION, set())
        format_selector = FormatSelector(phase_manager)

        format_without_pre_alloc = MockFixtureFormat({FixtureFillingPhase.FILL})

        assert not format_selector.should_generate(format_without_pre_alloc)

    def test_should_generate_single_phase_fill_only_format(self):
        """Test single-phase fill with fill-only format."""
        phase_manager = PhaseManager(FixtureFillingPhase.FILL, set())
        format_selector = FormatSelector(phase_manager)

        fill_only_format = MockFixtureFormat({FixtureFillingPhase.FILL})

        assert format_selector.should_generate(fill_only_format)

    def test_should_generate_single_phase_pre_alloc_format(self):
        """Test single-phase fill with format that supports pre-alloc."""
        phase_manager = PhaseManager(FixtureFillingPhase.FILL, set())
        format_selector = FormatSelector(phase_manager)

        format_with_pre_alloc = MockFixtureFormat(
            {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL}
        )

        # Should not generate because it needs pre-alloc but we're in single phase
        assert not format_selector.should_generate(format_with_pre_alloc)

    def test_should_generate_phase2_with_pre_alloc_format(self):
        """Test phase 2 (after pre-alloc) with format that supports pre-alloc."""
        phase_manager = PhaseManager(
            FixtureFillingPhase.FILL, {FixtureFillingPhase.PRE_ALLOC_GENERATION}
        )
        format_selector = FormatSelector(phase_manager)

        format_with_pre_alloc = MockFixtureFormat(
            {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL}
        )

        # Should generate in phase 2
        assert format_selector.should_generate(format_with_pre_alloc)

    def test_should_generate_phase2_without_pre_alloc_format(self):
        """Test phase 2 (after pre-alloc) with fill-only format."""
        phase_manager = PhaseManager(
            FixtureFillingPhase.FILL, {FixtureFillingPhase.PRE_ALLOC_GENERATION}
        )
        format_selector = FormatSelector(phase_manager)

        fill_only_format = MockFixtureFormat({FixtureFillingPhase.FILL})

        # Should not generate because it doesn't need pre-alloc
        assert not format_selector.should_generate(fill_only_format)

    def test_should_generate_phase2_with_generate_all(self):
        """Test phase 2 with --generate-all-formats flag."""
        phase_manager = PhaseManager(
            FixtureFillingPhase.FILL, {FixtureFillingPhase.PRE_ALLOC_GENERATION}
        )
        format_selector = FormatSelector(phase_manager)

        fill_only_format = MockFixtureFormat({FixtureFillingPhase.FILL})
        format_with_pre_alloc = MockFixtureFormat(
            {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL}
        )

        # With generate_all=True, both formats should be generated
        assert format_selector.should_generate(fill_only_format, generate_all=True)
        assert format_selector.should_generate(format_with_pre_alloc, generate_all=True)

    def test_should_generate_labeled_format(self):
        """Test with LabeledFixtureFormat wrapper."""
        phase_manager = PhaseManager(FixtureFillingPhase.FILL, set())
        format_selector = FormatSelector(phase_manager)

        labeled_format = MockLabeledFixtureFormat({FixtureFillingPhase.FILL})

        assert format_selector.should_generate(labeled_format)

    def test_should_generate_no_format_phases_attribute(self):
        """Test with object that has no format_phases attribute."""
        phase_manager = PhaseManager(FixtureFillingPhase.FILL, set())
        format_selector = FormatSelector(phase_manager)

        class SimpleFormat:
            pass

        # Should default to FILL phase only
        assert format_selector.should_generate(SimpleFormat())

    def test_comprehensive_scenarios(self):
        """Test comprehensive scenarios covering all phase and format combinations."""
        # Test matrix: (current_phase, previous_phases, format_phases, generate_all) -> expected
        test_cases = [
            # Pre-alloc generation phase
            (
                FixtureFillingPhase.PRE_ALLOC_GENERATION,
                set(),
                {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL},
                False,
                True,
            ),
            (
                FixtureFillingPhase.PRE_ALLOC_GENERATION,
                set(),
                {FixtureFillingPhase.FILL},
                False,
                False,
            ),
            # Single-phase fill
            (FixtureFillingPhase.FILL, set(), {FixtureFillingPhase.FILL}, False, True),
            (
                FixtureFillingPhase.FILL,
                set(),
                {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL},
                False,
                False,
            ),
            # Phase 2 without generate_all
            (
                FixtureFillingPhase.FILL,
                {FixtureFillingPhase.PRE_ALLOC_GENERATION},
                {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL},
                False,
                True,
            ),
            (
                FixtureFillingPhase.FILL,
                {FixtureFillingPhase.PRE_ALLOC_GENERATION},
                {FixtureFillingPhase.FILL},
                False,
                False,
            ),
            # Phase 2 with generate_all
            (
                FixtureFillingPhase.FILL,
                {FixtureFillingPhase.PRE_ALLOC_GENERATION},
                {FixtureFillingPhase.PRE_ALLOC_GENERATION, FixtureFillingPhase.FILL},
                True,
                True,
            ),
            (
                FixtureFillingPhase.FILL,
                {FixtureFillingPhase.PRE_ALLOC_GENERATION},
                {FixtureFillingPhase.FILL},
                True,
                True,
            ),
        ]

        for current, previous, format_phases, gen_all, expected in test_cases:
            phase_manager = PhaseManager(current, previous)
            format_selector = FormatSelector(phase_manager)
            fixture_format = MockFixtureFormat(format_phases)

            result = format_selector.should_generate(fixture_format, generate_all=gen_all)
            assert result == expected, (
                f"Failed for phase={current}, previous={previous}, "
                f"format_phases={format_phases}, generate_all={gen_all}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
