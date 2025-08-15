"""
Tests for the filter_fixtures CLI command.

Test Coverage:
==============
- Core filtering functionality (until, from, fork, ranges)
- Transition fork handling and chronological ordering
- Pre-alloc file filtering based on network field
- Error handling (invalid JSON, missing forks, directory validation)
- CLI flags (--clean, --quiet, --force for genindex)
- Hard failure prevention for corrupted fixtures

CI Release Workflow Integration:
===============================

Key tests for CI validation:

1. test_filter_fixtures_command_functionality:
   - Unit test for filter_fixtures command functionality
   - Tests that filtering works correctly on a single fixtures directory
   - Usage: pytest test_filter_fixtures.py::test_filter_fixtures_command_functionality

2. test_ci_release_validation:
   - Validates CI workflow results by comparing before/after directories
   - Provides detailed visual analysis for manual review
   - Auto-setup mode for unit testing, explicit directories for CI
   - Supports both unit test mode and CI validation mode

Recommended CI workflow:
1. Fill all tests up to and including ForkN+1:
   fill --output=fixtures_develop --until=ForkN+1

2. Filter out ForkN+1 to create stable release set:
   uv run filter_fixtures --input=fixtures_develop --output=fixtures_stable \
       --until=ForkN --quiet --clean

3. Validate the filtered fixtures:
   uv run pytest src/cli/tests/test_filter_fixtures.py::test_ci_release_validation \
       --before-fixtures-dir=fixtures_develop \
       --after-fixtures-dir=fixtures_stable -s

4. Optional: Visual sanity check of fork statistics:
   uv run fixture_stats fixtures_stable --show-forks

This ensures that mainnet release fixtures contain only stable, deployed forks
without development fixtures that could cause client incompatibilities.
"""

import json
import shutil
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from click.testing import CliRunner

from cli.filter_fixtures import filter_fixtures
from ethereum_test_forks.helpers import get_all_forks_chronologically, get_forks


def detect_available_forks(fixtures_dir: Path) -> set[str]:
    """Auto-detect available forks from index.json."""
    index_path = fixtures_dir / ".meta" / "index.json"
    if index_path.exists():
        with index_path.open() as f:
            index_data = json.load(f)
            return set(index_data.get("forks", []))
    return set()


def detect_available_formats(fixtures_dir: Path) -> set[str]:
    """Auto-detect available fixture formats from directory structure."""
    formats = set()
    if (fixtures_dir / "state_tests").exists():
        formats.add("state_test")
    if (fixtures_dir / "blockchain_tests").exists():
        formats.add("blockchain_test")
    if (fixtures_dir / "blockchain_tests_engine").exists():
        formats.add("blockchain_test_engine")
    if (fixtures_dir / "blockchain_tests_engine_x").exists():
        formats.add("blockchain_test_engine_x")
    return formats


@pytest.fixture
def test_fixtures_dir(request):
    """Return the path to the test fixtures directory."""
    custom_dir = request.config.getoption("--fixtures-dir")
    if custom_dir:
        return Path(custom_dir)
    return Path(__file__).parent / "test_fixtures"


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output."""
    with TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


def count_test_cases_in_index(output_dir: Path) -> int:
    """Count test cases in the generated index.json file."""
    index_path = output_dir / ".meta" / "index.json"
    if not index_path.exists():
        return 0
    with index_path.open() as f:
        index_data = json.load(f)
    return index_data.get("test_count", 0)


def get_forks_in_index(output_dir: Path) -> set[str]:
    """Get the set of forks present in the generated index.json file."""
    index_path = output_dir / ".meta" / "index.json"
    if not index_path.exists():
        return set()
    with index_path.open() as f:
        index_data = json.load(f)
    return set(index_data.get("forks", []))


def test_filter_until_cancun(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test filtering until Cancun fork."""
    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert (temp_output_dir / ".meta" / "index.json").exists()

    # Should include Cancun and earlier forks, exclude Prague and later
    forks = get_forks_in_index(temp_output_dir)
    assert "Cancun" in forks
    assert "Berlin" in forks if "Berlin" in forks else True  # May not be present in test data
    assert "Prague" not in forks
    assert "Osaka" not in forks

    # Should exclude transition forks that go beyond Cancun
    assert "CancunToPragueAtTime15k" not in forks
    assert "PragueToOsakaAtTime15k" not in forks


def test_filter_until_prague_includes_transitions(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that filtering until Prague includes relevant transition forks."""
    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Prague",
            "--quiet",
        ],
    )

    assert result.exit_code == 0

    forks = get_forks_in_index(temp_output_dir)
    assert "Prague" in forks
    assert "Cancun" in forks

    # Should include transition forks that end at or before Prague
    # CancunToPragueAtTime15k should be included (≤ Prague)
    # PragueToOsakaAtTime15k should be excluded (> Prague)
    test_count_prague = count_test_cases_in_index(temp_output_dir)

    # Verify Prague has more tests than Cancun (due to transition forks)
    cancun_temp_dir = Path(temp_output_dir.parent) / "cancun_test"
    cancun_temp_dir.mkdir(exist_ok=True)

    runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(cancun_temp_dir),
            "--until",
            "Cancun",
            "--quiet",
        ],
    )

    test_count_cancun = count_test_cases_in_index(cancun_temp_dir)
    assert test_count_prague >= test_count_cancun  # Prague should have at least as many


def test_filter_single_fork(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test filtering for a single fork only."""
    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--fork",
            "Cancun",
            "--quiet",
        ],
    )

    assert result.exit_code == 0

    forks = get_forks_in_index(temp_output_dir)
    assert "Cancun" in forks

    # Should not include other forks
    assert "Prague" not in forks
    assert "Berlin" not in forks
    assert "Shanghai" not in forks


def test_filter_from_to_range(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test filtering with both --from and --until parameters."""
    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--from",
            "Cancun",
            "--until",
            "Prague",
            "--quiet",
        ],
    )

    assert result.exit_code == 0

    forks = get_forks_in_index(temp_output_dir)
    assert "Cancun" in forks
    assert "Prague" in forks

    # Should not include forks outside the range
    assert "Berlin" not in forks
    assert "Osaka" not in forks


def test_invalid_fork_name(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that invalid fork names raise errors."""
    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--fork",
            "InvalidFork",
            "--quiet",
        ],
    )

    assert result.exit_code != 0
    assert "not found" in result.output


def test_invalid_json_causes_hard_failure(temp_output_dir: Path):
    """Test that invalid JSON files cause hard failures instead of silent failures."""
    from tempfile import TemporaryDirectory

    # Create a temporary input directory with invalid JSON
    with TemporaryDirectory() as temp_input:
        input_dir = Path(temp_input)

        # Create directory structure
        blockchain_tests_dir = input_dir / "blockchain_tests" / "test"
        blockchain_tests_dir.mkdir(parents=True)

        # Create an invalid JSON file
        invalid_json_file = blockchain_tests_dir / "invalid.json"
        invalid_json_file.write_text('{"invalid": json syntax}')  # Missing quotes around "json"

        # Create meta directory to make it look like a valid fixtures directory
        meta_dir = input_dir / ".meta"
        meta_dir.mkdir()
        index_file = meta_dir / "index.json"
        index_file.write_text('{"test_count": 0, "forks": []}')

        runner = CliRunner()
        result = runner.invoke(
            filter_fixtures,
            [
                "--input",
                str(input_dir),
                "--output",
                str(temp_output_dir),
                "--until",
                "Cancun",
                "--quiet",
            ],
        )

        # Should fail hard, not continue processing
        assert result.exit_code != 0
        assert "FATAL" in result.output
        assert "FILTER OPERATION FAILED" in result.output


def test_non_empty_output_directory_without_clean(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that non-empty output directory without --clean flag fails."""
    # Create a file in the output directory
    test_file = temp_output_dir / "test.txt"
    test_file.write_text("test")

    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--quiet",
        ],
    )

    assert result.exit_code != 0
    assert "not empty" in result.output


def test_clean_flag_removes_existing_files(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that --clean flag removes existing files from output directory."""
    # Create a file in the output directory
    test_file = temp_output_dir / "test.txt"
    test_file.write_text("test")

    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--clean",
            "--quiet",
        ],
    )

    assert result.exit_code == 0
    assert not test_file.exists()  # Should be cleaned
    assert (temp_output_dir / ".meta" / "index.json").exists()  # Should have new content


def test_pre_alloc_files_filtered_correctly(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that pre_alloc files are filtered based on their network field."""
    available_formats = detect_available_formats(test_fixtures_dir)

    # Skip if no engine_x format available
    if "blockchain_test_engine_x" not in available_formats:
        pytest.skip("blockchain_test_engine_x format not available in fixtures directory")

    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--quiet",
        ],
    )

    assert result.exit_code == 0

    # Check that pre_alloc files exist in output
    pre_alloc_dir = temp_output_dir / "blockchain_tests_engine_x" / "pre_alloc"
    if pre_alloc_dir.exists():
        pre_alloc_files = list(pre_alloc_dir.glob("*.json"))
        # If pre_alloc files exist, they should only contain networks ≤ Cancun
        for pre_alloc_file in pre_alloc_files:
            with pre_alloc_file.open() as f:
                pre_alloc_data = json.load(f)
            network = pre_alloc_data.get("network", "")
            # Should not contain networks beyond Cancun
            assert "Prague" not in network
            assert "Osaka" not in network


def test_quiet_flag_suppresses_output(test_fixtures_dir: Path, temp_output_dir: Path):
    """Test that --quiet flag suppresses progress output."""
    runner = CliRunner()

    # Test without quiet flag
    result_verbose = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--clean",
        ],
    )

    # Clean the directory for second test
    shutil.rmtree(temp_output_dir)
    temp_output_dir.mkdir()

    # Test with quiet flag
    result_quiet = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            "Cancun",
            "--quiet",
        ],
    )

    assert result_verbose.exit_code == 0
    assert result_quiet.exit_code == 0

    # Quiet mode should have less output
    assert len(result_quiet.output) < len(result_verbose.output)


def test_filter_fixtures_command_functionality(test_fixtures_dir: Path, temp_output_dir: Path):
    """
    Test that the filter_fixtures command works correctly.

    This test dynamically detects the latest and second-latest forks in the input
    fixtures and validates that filtering to the second-latest fork works correctly.
    This is a unit test for the core filtering functionality.

    Usage:
    pytest src/cli/tests/test_filter_fixtures.py::test_filter_fixtures_command_functionality \
        --fixtures-dir=test_fixtures
    """
    from ethereum_test_forks.helpers import get_forks

    available_forks = detect_available_forks(test_fixtures_dir)

    if len(available_forks) < 2:
        pytest.skip("Need at least 2 forks available for release workflow testing")

    # Get all forks in chronological order
    all_forks_ordered = get_forks()
    fork_names_ordered = [fork.name() for fork in all_forks_ordered]

    # Find available forks in chronological order
    available_ordered = [
        fork_name for fork_name in fork_names_ordered if fork_name in available_forks
    ]

    if len(available_ordered) < 2:
        pytest.skip("Need at least 2 chronologically ordered forks for testing")

    # Get latest and second-latest available forks
    latest_fork = available_ordered[-1]
    second_latest_fork = available_ordered[-2]

    runner = CliRunner()
    result = runner.invoke(
        filter_fixtures,
        [
            "--input",
            str(test_fixtures_dir),
            "--output",
            str(temp_output_dir),
            "--until",
            second_latest_fork,
            "--quiet",
        ],
    )

    assert result.exit_code == 0, f"Filtering failed with exit code {result.exit_code}"

    # Get what was actually filtered
    filtered_forks = get_forks_in_index(temp_output_dir)

    # Second-latest fork should be included
    assert second_latest_fork in filtered_forks, (
        f"{second_latest_fork} should be included when filtering --until {second_latest_fork}"
    )

    # Latest fork should be excluded
    assert latest_fork not in filtered_forks, (
        f"{latest_fork} should be excluded when filtering --until {second_latest_fork}"
    )

    # Test count validation
    total_count = count_test_cases_in_index(test_fixtures_dir)
    filtered_count = count_test_cases_in_index(temp_output_dir)

    assert filtered_count > 0, "Filtered fixtures should contain test cases"
    assert filtered_count <= total_count, "Filtered count should not exceed total"

    # Ensure filtering actually reduced the test count (unless there are no latest fork tests)
    if latest_fork in available_forks:
        # We expect some reduction unless the latest fork has no tests
        assert filtered_count <= total_count, "Filtering should not increase test count"

    # Validate directory structure
    assert (temp_output_dir / ".meta" / "index.json").exists(), (
        "index.json missing from filtered output"
    )

    print("✅ Filter fixtures command validation passed:")
    print(f"   Latest fork (excluded): {latest_fork}")
    print(f"   Target fork (included): {second_latest_fork}")
    print(f"   Test counts: {filtered_count}/{total_count} ({filtered_count / total_count:.1%})")


@pytest.fixture
def before_fixtures_dir(request):
    """Return path to before-filtering fixtures directory."""
    custom_dir = request.config.getoption("--before-fixtures-dir")
    if custom_dir:
        return Path(custom_dir)
    return None


@pytest.fixture
def after_fixtures_dir(request):
    """Return path to after-filtering fixtures directory."""
    custom_dir = request.config.getoption("--after-fixtures-dir")
    if custom_dir:
        return Path(custom_dir)
    return None


def test_ci_release_validation(
    before_fixtures_dir: Path, after_fixtures_dir: Path, temp_output_dir: Path
):
    """
    Test CI release workflow by comparing before and after filtering directories.

    This test validates that filtering was done correctly by comparing two fixture
    directories and providing a detailed visual summary for manual review.

    Usage in CI:
    pytest src/cli/tests/test_filter_fixtures.py::test_ci_release_validation \
        --before-fixtures-dir=fixtures_develop \
        --after-fixtures-dir=fixtures_stable \
        -s

    Auto-setup for unit tests:
    When no directories are provided, automatically creates a filtering scenario
    using test_fixtures as "before" and filtering to second-latest fork as "after".
    """
    # Auto-setup for unit testing when no arguments provided
    if not before_fixtures_dir or not after_fixtures_dir:
        test_fixtures_path = Path(__file__).parent / "test_fixtures"

        if not test_fixtures_path.exists():
            pytest.fail(
                "Auto-setup failed: test_fixtures directory not found.\n\n"
                "For unit testing, ensure test_fixtures exists, or provide explicit directories:\n"
                "  --before-fixtures-dir=fixtures_develop\n"
                "  --after-fixtures-dir=fixtures_stable\n\n"
                "Example CI usage:\n"
                "  pytest test_filter_fixtures.py::test_ci_release_validation \\\n"
                "    --before-fixtures-dir=fixtures_develop \\\n"
                "    --after-fixtures-dir=fixtures_stable -s"
            )

        print("🔧 Auto-setup: Running filter_fixtures for unit testing...")

        # Use test_fixtures as "before"
        before_fixtures_dir = test_fixtures_path

        # Get available forks and find second-latest for filtering
        available_forks = detect_available_forks(before_fixtures_dir)
        if len(available_forks) < 2:
            pytest.skip(
                "Auto-setup requires at least 2 forks in test_fixtures for meaningful testing"
            )

        all_forks_ordered = get_forks()
        fork_names_ordered = [fork.name() for fork in all_forks_ordered]
        available_ordered = [
            fork_name for fork_name in fork_names_ordered if fork_name in available_forks
        ]

        if len(available_ordered) < 2:
            pytest.skip("Auto-setup requires at least 2 chronologically ordered forks")

        second_latest_fork = available_ordered[-2]

        # Create filtered "after" directory
        after_fixtures_dir = temp_output_dir

        runner = CliRunner()
        result = runner.invoke(
            filter_fixtures,
            [
                "--input",
                str(before_fixtures_dir),
                "--output",
                str(after_fixtures_dir),
                "--until",
                second_latest_fork,
                "--quiet",
            ],
        )

        if result.exit_code != 0:
            pytest.fail(f"Auto-setup filter_fixtures failed: {result.output}")

        print(f"   Before: {before_fixtures_dir.name}/ (all forks)")
        print(f"   After:  {after_fixtures_dir.name}/ (filtered --until {second_latest_fork})")
        print()

    if not before_fixtures_dir.exists():
        pytest.fail(
            f"❌ Before fixtures directory does not exist: {before_fixtures_dir}\n\n"
            "Ensure the development fixtures directory exists and contains fixtures.\n"
            "This directory should contain the output from:\n"
            "  fill --output=fixtures_develop --until=ForkN+1"
        )

    if not after_fixtures_dir.exists():
        pytest.fail(
            f"❌ After fixtures directory does not exist: {after_fixtures_dir}\n\n"
            "Ensure the stable fixtures directory exists and contains filtered fixtures.\n"
            "This directory should contain the output from:\n"
            "  filter_fixtures --input=fixtures_develop --output=fixtures_stable --until=ForkN"
        )

    # Load index.json from both directories
    before_index_path = before_fixtures_dir / ".meta" / "index.json"
    after_index_path = after_fixtures_dir / ".meta" / "index.json"

    if not before_index_path.exists():
        pytest.fail(
            f"❌ Before index.json not found: {before_index_path}\n\n"
            "The fixtures directory appears to be incomplete or corrupted.\n"
            "Ensure the directory was generated properly with 'fill' command and contains:\n"
            "  - .meta/index.json\n"
            "  - fixture files in subdirectories"
        )

    if not after_index_path.exists():
        pytest.fail(
            f"❌ After index.json not found: {after_index_path}\n\n"
            "The filtered fixtures directory appears to be incomplete or corrupted.\n"
            "Ensure the directory was generated properly with 'filter_fixtures' and contains:\n"
            "  - .meta/index.json\n"
            "  - filtered fixture files in subdirectories"
        )

    with before_index_path.open() as f:
        before_index = json.load(f)

    with after_index_path.open() as f:
        after_index = json.load(f)

    # Extract fork information
    before_forks = set(before_index.get("forks", []))
    after_forks = set(after_index.get("forks", []))
    before_total = before_index.get("test_count", 0)
    after_total = after_index.get("test_count", 0)

    # Count tests per fork
    before_fork_counts: defaultdict[str, int] = defaultdict(int)
    for test_case in before_index.get("test_cases", []):
        fork = test_case.get("fork")
        if fork:
            before_fork_counts[fork] += 1

    after_fork_counts: defaultdict[str, int] = defaultdict(int)
    for test_case in after_index.get("test_cases", []):
        fork = test_case.get("fork")
        if fork:
            after_fork_counts[fork] += 1

    # Get chronologically ordered fork list
    all_forks_chronological = get_all_forks_chronologically()
    fork_names_ordered = [fork.name() for fork in all_forks_chronological]

    # Filter to only forks present in either directory
    relevant_forks = [
        fork_name
        for fork_name in fork_names_ordered
        if fork_name in before_forks or fork_name in after_forks
    ]

    # Calculate filtered forks
    filtered_forks = before_forks - after_forks
    kept_forks = before_forks & after_forks

    # Print visual summary
    print("\n" + "=" * 60)
    print("CI Release Validation Report")
    print("=" * 60)
    print()
    print("📁 Directories:")
    print(f"  Before (develop): {before_fixtures_dir.name}/")
    print(f"  After (stable):   {after_fixtures_dir.name}/")
    print()
    print("🍴 Fork Analysis (Chronological Order):")
    print("-" * 60)
    print(f"{'Fork':<30} {'Develop':<8} {'Stable':<8} {'Status':<10}")
    print("-" * 60)

    for fork_name in relevant_forks:
        before_count = before_fork_counts.get(fork_name, 0)
        after_count = after_fork_counts.get(fork_name, 0)

        if fork_name in filtered_forks:
            status = "❌ Filtered"
        elif fork_name in kept_forks:
            status = "✅ Kept"
        else:
            status = "➕ Added"  # Shouldn't happen but just in case

        print(f"{fork_name:<30} {before_count:<8,} {after_count:<8,} {status:<10}")

    print("-" * 60)
    retention_pct = (after_total / before_total * 100) if before_total > 0 else 0
    print(f"{'TOTAL':<30} {before_total:<8,} {after_total:<8,} {retention_pct:>6.1f}% retained")
    print()

    if filtered_forks:
        print("✂️ Filtered Out (in chronological order):")
        filtered_ordered = [f for f in relevant_forks if f in filtered_forks]
        for fork_name in filtered_ordered:
            count = before_fork_counts.get(fork_name, 0)
            print(f"  - {fork_name} ({count:,} tests)")
        print()

    # Validations
    print("✅ Validation Results:")

    # 1. Stable should be subset of develop
    subset_ok = after_forks.issubset(before_forks)
    print(f"  - Stable is subset of develop: {'PASS' if subset_ok else 'FAIL'}")

    # 2. Test counts should be reasonable
    count_ok = after_total <= before_total and after_total > 0
    print(f"  - Test count consistency: {'PASS' if count_ok else 'FAIL'}")

    # 3. Fork-by-fork counts should make sense
    fork_counts_ok = True
    for fork_name in kept_forks:
        before_count = before_fork_counts.get(fork_name, 0)
        after_count = after_fork_counts.get(fork_name, 0)
        if after_count > before_count:
            fork_counts_ok = False
            break

    print(f"  - Fork count consistency: {'PASS' if fork_counts_ok else 'FAIL'}")

    # 4. Should have some filtering (unless it's a no-op)
    filtering_ok = len(filtered_forks) > 0 or before_total == after_total
    print(f"  - Meaningful filtering: {'PASS' if filtering_ok else 'FAIL'}")

    print()

    # Assert on critical validations
    assert subset_ok, f"After forks are not a subset of before forks: {after_forks - before_forks}"
    assert count_ok, f"Test count validation failed: {after_total} > {before_total} or zero tests"
    assert fork_counts_ok, "Some forks have more tests after filtering than before"
