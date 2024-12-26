"""
Procedures to consume fixtures from Github releases.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

import platformdirs
import requests
from pydantic import BaseModel, Field, RootModel

RELEASE_INFORMATION_URL = "https://api.github.com/repos/ethereum/execution-spec-tests/releases"


CACHED_RELEASE_INFORMATION_FILE = (
    Path(platformdirs.user_cache_dir("ethereum-execution-spec-tests")) / "release_information.json"
)


class NoSuchRelease(Exception):
    """
    Raised when a release does not exist.
    """

    def __init__(self, release_source: str):
        super().__init__(f"Unknown release source: {release_source}")


class AssetNotFound(Exception):
    """
    Raised when a release has no assets.
    """

    def __init__(self, release_source: str):
        super().__init__(f"Asset not found: {release_source}")


class ReleaseDescriptor:
    """
    A descriptor for a release.
    """

    tag_name: str
    version: str | None

    def __init__(self, release_source: str):
        if "@" in release_source:
            self.tag_name, self.version = release_source.split("@")
            if self.version == "" or self.version == "latest":
                self.version = None
        else:
            self.tag_name = release_source
            self.version = None

    def __eq__(self, value) -> bool:
        """
        Check if the release descriptor matches the value.

        Returns True if the value is the same as the tag name or the tag name and version.
        """
        assert isinstance(value, str), f"Expected a string, but got: {value}"
        if self.version is not None:
            return value == f"{self.tag_name}@{self.version}"
        return value.startswith(self.tag_name)

    @property
    def asset_name(self) -> str:
        """
        Get the asset name.
        """
        return f"fixtures_{self.tag_name}.tar.gz"


class Asset(BaseModel):
    """
    Information about a release asset.
    """

    url: str = Field(..., alias="browser_download_url")
    id: int
    name: str
    content_type: str
    size: int


class Assets(RootModel[List[Asset]]):
    """
    A list of assets and their information.
    """

    root: List[Asset]

    def __contains__(self, release_descriptor: ReleaseDescriptor) -> bool:
        """
        Check if the assets contain the release descriptor.
        """
        return any(release_descriptor.asset_name == asset.name for asset in self.root)


class ReleaseInformation(BaseModel):
    """
    Information about a release.
    """

    url: str = Field(..., alias="html_url")
    id: int
    tag_name: str
    name: str
    created_at: datetime
    published_at: datetime
    assets: Assets

    def __contains__(self, release_descriptor: ReleaseDescriptor) -> bool:
        """
        Check if the release information contains the release descriptor.
        """
        if release_descriptor.version is not None:
            return release_descriptor == self.tag_name
        for asset in self.assets.root:
            if asset.name == release_descriptor.asset_name:
                return True
        return False

    def get_asset(self, release_descriptor: ReleaseDescriptor) -> Asset:
        """
        Get the asset URL.
        """
        for asset in self.assets.root:
            if asset.name == release_descriptor.asset_name:
                return asset
        raise AssetNotFound(release_descriptor.tag_name)


class Releases(RootModel[List[ReleaseInformation]]):
    """
    A list of releases and their information.
    """

    root: List[ReleaseInformation]


def is_docker_or_ci() -> bool:
    """
    Check if the code is running inside a Docker container or a CI environment.
    """
    return "GITHUB_ACTIONS" in os.environ or Path("/.dockerenv").exists()


def parse_release_information(release_information: dict) -> List[ReleaseInformation]:
    """
    Parse the release information from the Github API.
    """
    return Releases.model_validate(release_information).root  # type: ignore


def download_release_information(destination_file: Path | None) -> List[ReleaseInformation]:
    """
    Download the latest stable and develop releases and optionally save them to a file.
    """
    response = requests.get(RELEASE_INFORMATION_URL)
    response.raise_for_status()
    release_information = response.json()
    if destination_file is not None:
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_file, "w") as file:
            json.dump(release_information, file)
    return parse_release_information(release_information)


def parse_release_information_from_file(
    release_information_file: Path,
) -> List[ReleaseInformation]:
    """
    Parse the release information from a file.
    """
    with open(release_information_file, "r") as file:
        release_information = json.load(file)
    return parse_release_information(release_information)


def get_release_url_from_release_information(
    release_source: str, release_information: List[ReleaseInformation]
) -> str:
    """
    Get the URL for a specific release.
    """
    release_descriptor = ReleaseDescriptor(release_source)
    for release in release_information:
        if release_descriptor in release:
            return release.get_asset(release_descriptor).url
    raise NoSuchRelease(release_source)


def get_release_information() -> List[ReleaseInformation]:
    """
    Get the release information.

    First check if the cached release information file exists. If it does, but it is older than 4
    hours, delete the file, unless running inside a CI environment or a Docker container.
    Then download the release information from the Github API and save it to the cache file.
    """
    if CACHED_RELEASE_INFORMATION_FILE.exists():
        last_modified = CACHED_RELEASE_INFORMATION_FILE.stat().st_mtime
        if (datetime.now().timestamp() - last_modified) < 4 * 60 * 60 or is_docker_or_ci():
            return parse_release_information_from_file(CACHED_RELEASE_INFORMATION_FILE)
        CACHED_RELEASE_INFORMATION_FILE.unlink()
    if not CACHED_RELEASE_INFORMATION_FILE.exists():
        return download_release_information(CACHED_RELEASE_INFORMATION_FILE)
    return parse_release_information_from_file(CACHED_RELEASE_INFORMATION_FILE)


def get_release_url(release_source: str) -> str:
    """
    Get the URL for a specific release.
    """
    release_information = get_release_information()
    return get_release_url_from_release_information(release_source, release_information)
