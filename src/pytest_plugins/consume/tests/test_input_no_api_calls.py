"""Test the --no-api-calls flag functionality for consume cache command."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest_plugins.consume.consume import FixturesSource


class TestNoApiCallsFlag:
    """Test suite for the --no-api-calls flag."""

    def test_fixtures_source_from_release_url_without_flag(self):
        """Test that API calls are made when no_api_calls=False."""
        test_url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"

        with patch("pytest_plugins.consume.consume.get_release_page_url") as mock_get_page:
            mock_get_page.return_value = (
                "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
            )
            with patch("pytest_plugins.consume.consume.FixtureDownloader") as mock_downloader:
                mock_instance = MagicMock()
                mock_instance.download_and_extract.return_value = (False, Path("/tmp/test"))
                mock_downloader.return_value = mock_instance

                source = FixturesSource.from_release_url(test_url, no_api_calls=False)

                # Verify API call was made
                mock_get_page.assert_called_once_with(test_url, no_api_calls=False)
                assert (
                    source.release_page
                    == "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
                )

    def test_fixtures_source_from_release_url_with_flag(self):
        """Test that API calls are skipped when no_api_calls=True."""
        test_url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"

        with patch("pytest_plugins.consume.consume.get_release_page_url") as mock_get_page:
            # Return empty string when no_api_calls=True and no cache
            mock_get_page.return_value = ""
            with patch("pytest_plugins.consume.consume.FixtureDownloader") as mock_downloader:
                mock_instance = MagicMock()
                mock_instance.download_and_extract.return_value = (False, Path("/tmp/test"))
                mock_downloader.return_value = mock_instance

                source = FixturesSource.from_release_url(test_url, no_api_calls=True)

                # Verify API call was made with no_api_calls=True
                mock_get_page.assert_called_once_with(test_url, no_api_calls=True)
                # The mock should return empty string when no_api_calls=True and no cache
                assert source.release_page == ""

    def test_fixtures_source_from_release_url_with_flag_but_cached(self):
        """Test that cached release page is returned even when no_api_calls=True."""
        test_url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"

        with patch("pytest_plugins.consume.consume.get_release_page_url") as mock_get_page:
            # Simulate cached data being available - function returns the release page
            mock_get_page.return_value = (
                "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
            )
            with patch("pytest_plugins.consume.consume.FixtureDownloader") as mock_downloader:
                mock_instance = MagicMock()
                mock_instance.download_and_extract.return_value = (False, Path("/tmp/test"))
                mock_downloader.return_value = mock_instance

                source = FixturesSource.from_release_url(test_url, no_api_calls=True)

                # Verify the function was called with no_api_calls=True
                mock_get_page.assert_called_once_with(test_url, no_api_calls=True)
                # But release page is still returned because it was cached
                assert (
                    source.release_page
                    == "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
                )

    def test_fixtures_source_from_release_spec_always_makes_api_calls(self):
        """Test that release specs always make API calls (no no_api_calls parameter)."""
        test_spec = "stable@latest"

        with patch("pytest_plugins.consume.consume.get_release_url") as mock_get_url:
            mock_get_url.return_value = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_stable.tar.gz"
            with patch("pytest_plugins.consume.consume.get_release_page_url") as mock_get_page:
                mock_get_page.return_value = (
                    "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
                )
                with patch("pytest_plugins.consume.consume.FixtureDownloader") as mock_downloader:
                    mock_instance = MagicMock()
                    mock_instance.download_and_extract.return_value = (False, Path("/tmp/test"))
                    mock_downloader.return_value = mock_instance

                    source = FixturesSource.from_release_spec(test_spec)

                    # Verify API calls were made (both for URL resolution and release page)
                    mock_get_url.assert_called_once_with(test_spec)
                    mock_get_page.assert_called_once_with(
                        "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_stable.tar.gz",
                        no_api_calls=False,
                    )
                    assert (
                        source.release_page
                        == "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
                    )

    def test_output_formatting_with_release_page(self):
        """Test output formatting when release page is present."""
        from unittest.mock import MagicMock

        from pytest import Config

        config = MagicMock(spec=Config)
        config.fixtures_source = MagicMock()
        config.fixtures_source.was_cached = False
        config.fixtures_source.is_local = False
        config.fixtures_source.path = Path("/tmp/test")
        config.fixtures_source.url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"
        config.fixtures_source.release_page = (
            "https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
        )

        # Simulate the output generation logic from pytest_configure
        reason = ""
        if config.fixtures_source.was_cached:
            reason += "Fixtures already cached."
        elif not config.fixtures_source.is_local:
            reason += "Fixtures downloaded and cached."
        reason += f"\nPath: {config.fixtures_source.path}"
        reason += f"\nInput: {config.fixtures_source.url or config.fixtures_source.path}"
        if config.fixtures_source.release_page:
            reason += f"\nRelease page: {config.fixtures_source.release_page}"

        assert (
            "Release page: https://github.com/ethereum/execution-spec-tests/releases/tag/v3.0.0"
            in reason
        )

    def test_output_formatting_without_release_page(self):
        """Test output formatting when release page is empty (no_api_calls=True)."""
        from unittest.mock import MagicMock

        from pytest import Config

        config = MagicMock(spec=Config)
        config.fixtures_source = MagicMock()
        config.fixtures_source.was_cached = False
        config.fixtures_source.is_local = False
        config.fixtures_source.path = Path("/tmp/test")
        config.fixtures_source.url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"
        config.fixtures_source.release_page = ""  # Empty when no_api_calls=True

        # Simulate the output generation logic from pytest_configure
        reason = ""
        if config.fixtures_source.was_cached:
            reason += "Fixtures already cached."
        elif not config.fixtures_source.is_local:
            reason += "Fixtures downloaded and cached."
        reason += f"\nPath: {config.fixtures_source.path}"
        reason += f"\nInput: {config.fixtures_source.url or config.fixtures_source.path}"
        if config.fixtures_source.release_page:
            reason += f"\nRelease page: {config.fixtures_source.release_page}"

        assert "Release page:" not in reason
        assert "Path:" in reason
        assert "Input:" in reason


class TestFixturesSourceFromInput:
    """Test the from_input method with the no_api_calls parameter."""

    def test_from_input_propagates_no_api_calls_for_release_url(self):
        """Test that from_input passes no_api_calls to from_release_url."""
        test_url = "https://github.com/ethereum/execution-spec-tests/releases/download/v3.0.0/fixtures_develop.tar.gz"

        with patch.object(FixturesSource, "from_release_url") as mock_from_release_url:
            mock_from_release_url.return_value = MagicMock()

            FixturesSource.from_input(test_url, no_api_calls=True)

            mock_from_release_url.assert_called_once_with(test_url, no_api_calls=True)

    def test_from_input_does_not_pass_no_api_calls_for_release_spec(self):
        """Test that from_input does not pass no_api_calls to from_release_spec."""
        test_spec = "stable@latest"

        with patch.object(FixturesSource, "from_release_spec") as mock_from_release_spec:
            mock_from_release_spec.return_value = MagicMock()

            FixturesSource.from_input(test_spec, no_api_calls=True)

            # from_release_spec no longer accepts no_api_calls parameter
            mock_from_release_spec.assert_called_once_with(test_spec)

    def test_from_input_regular_url_ignores_no_api_calls(self):
        """Test that from_input for non-GitHub URLs doesn't use no_api_calls."""
        test_url = "http://example.com/fixtures.tar.gz"

        with patch.object(FixturesSource, "from_url") as mock_from_url:
            mock_from_url.return_value = MagicMock()

            FixturesSource.from_input(test_url, no_api_calls=True)

            # from_url doesn't accept no_api_calls parameter
            mock_from_url.assert_called_once_with(test_url)
