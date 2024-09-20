"""
Fixture formats enum.
"""
from enum import Enum
from pathlib import Path


class FixtureFormats(Enum):
    """
    Helper class to define fixture formats.
    """

    UNSET_TEST_FORMAT = "unset_test_format"
    STATE_TEST = "state_test"
    BLOCKCHAIN_TEST = "blockchain_test"
    BLOCKCHAIN_TEST_ENGINE = "blockchain_test_engine"
    EOF_TEST = "eof_test"

    def is_state_test(self):  # noqa: D102
        return self == FixtureFormats.STATE_TEST

    def is_blockchain_test(self):  # noqa: D102
        return self in (FixtureFormats.BLOCKCHAIN_TEST, FixtureFormats.BLOCKCHAIN_TEST_ENGINE)

    def is_hive_format(self):  # noqa: D102
        return self == FixtureFormats.BLOCKCHAIN_TEST_ENGINE

    def is_standard_format(self):  # noqa: D102
        return self in (FixtureFormats.STATE_TEST, FixtureFormats.BLOCKCHAIN_TEST)

    def is_verifiable(self):  # noqa: D102
        return self in (FixtureFormats.STATE_TEST, FixtureFormats.BLOCKCHAIN_TEST)

    def description(self):
        """
        Returns a description of the fixture format.

        Used to add a description to the generated pytest marks.
        """
        if self == FixtureFormats.UNSET_TEST_FORMAT:
            return "Unknown fixture format; it has not been set."
        elif self == FixtureFormats.STATE_TEST:
            return "Tests that generate a state test fixture."
        elif self == FixtureFormats.BLOCKCHAIN_TEST:
            return "Tests that generate a blockchain test fixture."
        elif self == FixtureFormats.BLOCKCHAIN_TEST_ENGINE:
            return "Tests that generate a blockchain test fixture in Engine API format."
        elif self == FixtureFormats.EOF_TEST:
            return "Tests that generate an EOF test fixture."
        raise Exception(f"Unknown fixture format: {format}.")

    @property
    def output_base_dir_name(self) -> Path:
        """
        Returns the name of the subdirectory where this type of fixture should be dumped to.
        """
        return Path(self.value.replace("test", "tests"))

    @property
    def output_file_extension(self) -> str:
        """
        Returns the file extension for this type of fixture.

        By default, fixtures are dumped as JSON files.
        """
        return ".json"
