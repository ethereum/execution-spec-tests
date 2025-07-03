"""Test the --generate-all-formats functionality."""

from pytest_plugins.filler.fixture_output import FixtureOutput


def test_fixture_output_with_generate_all_formats():
    """Test that FixtureOutput properly handles the generate_all_formats parameter."""
    # Test with generate_all_formats=True
    fixture_output = FixtureOutput(
        output_path="/tmp/test",
        generate_all_formats=True,
    )
    assert fixture_output.generate_all_formats is True

    # Test with generate_all_formats=False (default)
    fixture_output = FixtureOutput(
        output_path="/tmp/test",
    )
    assert fixture_output.generate_all_formats is False


def test_fixture_output_from_config_includes_generate_all_formats():
    """Test that FixtureOutput.from_config includes the generate_all_formats option."""

    # Mock pytest config object
    class MockConfig:
        def getoption(self, option):
            option_values = {
                "output": "/tmp/test",
                "flat_output": False,
                "single_fixture_per_file": False,
                "clean": False,
                "generate_pre_alloc_groups": False,
                "use_pre_alloc_groups": False,
                "generate_all_formats": True,  # Test the new option
            }
            return option_values.get(option, False)

    config = MockConfig()
    fixture_output = FixtureOutput.from_config(config)

    assert fixture_output.generate_all_formats is True
    assert fixture_output.output_path.name == "test"
