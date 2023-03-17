"""
Types used to describe a reference specification and versioning used to write
Ethereum tests.
"""

import base64
import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

import requests


# Exceptions
class NoLatestKnownVersion(Exception):
    pass


class ReferenceSpec:
    """
    Reference Specification Description Abstract Class.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the spec.
        """
        pass

    @abstractmethod
    def has_known_version(self) -> bool:
        """
        Returns true if the reference spec object is hard-coded with a latest
        known version.
        """
        pass

    @abstractmethod
    def known_version(self) -> str:
        """
        Returns the latest known version in the reference.
        """
        pass

    @abstractmethod
    def latest_version(self) -> str:
        """
        Returns a digest that points to the latest version of the spec.
        """
        pass

    @abstractmethod
    def is_outdated(self) -> bool:
        """
        Checks whether the reference specification has been updated since the
        test was last updated.
        """
        pass

    @abstractmethod
    def write_info(self, info: Dict[str, str]):
        """
        Writes info about the reference specification used into the output
        fixture.
        """
        pass


def decode_base64_content(encoded_data: str) -> str:
    return base64.b64decode(encoded_data).decode("utf-8")


@dataclass(kw_only=True)
class GitReferenceSpec(ReferenceSpec):
    """
    Git Reference Specification Description Class
    """

    SpecPath: str
    RepoOwner: str = "ethereum"
    RepoName: str = "EIPs"
    BranchName: str = "master"
    SpecVersion: str = ""
    _latest_spec: Dict | None = None

    def name(self) -> str:
        """
        Returns the name of the spec.
        """
        return (
            f"https://github.com/{self.RepoOwner}/"
            + f"{self.RepoName}/blob/{self.BranchName}/{self.SpecPath}"
        )

    def known_version(self) -> str:
        """
        Returns the latest known version in the reference.
        """
        return self.SpecVersion

    def latest_known_spec(self) -> Dict | None:
        response = requests.get(
            f"https://api.github.com/repos/{self.RepoOwner}/"
            + f"{self.RepoName}/git/blobs/{self.SpecVersion}"
        )
        if response.status_code != 200:
            return None
        content = json.loads(response.content)
        content["content"] = decode_base64_content(content["content"])
        return content

    def latest_spec(self) -> Dict:
        if self._latest_spec is not None:
            return self._latest_spec
        response = requests.get(
            f"https://api.github.com/repos/{self.RepoOwner}/"
            + f"{self.RepoName}/contents/{self.SpecPath}"
        )
        if response.status_code != 200:
            return None
        content = json.loads(response.content)
        content["content"] = decode_base64_content(content["content"])
        self._latest_spec = content
        return content

    def is_outdated(self) -> bool:
        if self.SpecVersion == "":
            raise NoLatestKnownVersion
        # Fetch the latest spec
        latest = self.latest_spec()
        if latest is None:
            raise Exception("unable to get latest version")
        return latest["sha"].strip() != self.SpecVersion.strip()

    def latest_version(self) -> str:
        """
        Returns the sha digest of the latest version of the spec.
        """
        latest = self.latest_spec()
        if latest is None or "sha" not in latest:
            return ""
        return latest["sha"]

    def has_known_version(self) -> bool:
        """
        Returns true if the reference spec object is hard-coded with a latest
        known version.
        """
        return self.SpecVersion != ""

    def write_info(self, info: Dict[str, str]):
        """
        Writes info about the reference specification used into the output
        fixture.
        """
        info["reference-spec"] = self.name()
        info["reference-spec-version"] = self.SpecVersion


_ = GitReferenceSpec(SpecPath="")
