"""Reference Specification file located in a github repository."""

import base64
import json
import warnings
from dataclasses import dataclass
from typing import Any, Dict

import requests

from .reference_spec import NoLatestKnownVersionError, ParseModuleError, ReferenceSpec


def _decode_base64_content(encoded_data: str) -> str:
    return base64.b64decode(encoded_data).decode("utf-8")


@dataclass(kw_only=True)
class GitReferenceSpec(ReferenceSpec):
    """Git Reference Specification Description Class."""

    SpecPath: str
    RepositoryOwner: str = "ethereum"
    RepositoryName: str = "EIPs"
    BranchName: str = "master"
    SpecVersion: str = ""
    _latest_spec: Dict | None = None

    def name(self) -> str:
        """Return the name of the spec."""
        return (
            f"https://github.com/{self.RepositoryOwner}/"
            + f"{self.RepositoryName}/blob/{self.BranchName}/{self.SpecPath}"
        )

    def known_version(self) -> str:
        """Return the latest known version in the reference."""
        return self.SpecVersion

    def api_url(self) -> str:
        """URL used to retrieve the version via the Github API."""
        return (
            f"https://api.github.com/repos/{self.RepositoryOwner}/"
            f"{self.RepositoryName}/contents/{self.SpecPath}"
        )

    def _get_latest_known_spec(self) -> Dict | None:
        response = requests.get(self.api_url())
        if response.status_code != 200:
            return None
        content = json.loads(response.content)
        content["content"] = _decode_base64_content(content["content"])
        return content

    def _get_latest_spec(self) -> Dict | None:
        if self._latest_spec is not None:
            return self._latest_spec
        response = requests.get(self.api_url())
        if response.status_code != 200:
            warnings.warn(
                f"Unable to get latest version, status code: {response.status_code} - "
                f"text: {response.text}",
                stacklevel=2,
            )
            return None
        content = json.loads(response.content)
        content["content"] = _decode_base64_content(content["content"])
        self._latest_spec = content
        return content

    def is_outdated(self) -> bool:
        """
        Check whether the reference specification has been updated since the
        test was last updated, by comparing the latest known `sha` value of
        the file in the repository.
        """
        if self.SpecVersion == "":
            raise NoLatestKnownVersionError
        # Fetch the latest spec
        latest = self._get_latest_spec()
        if latest is None:
            raise Exception("unable to get latest version")
        return latest["sha"].strip() != self.SpecVersion.strip()

    def latest_version(self) -> str:
        """Return the sha digest of the latest version of the spec."""
        latest = self._get_latest_spec()
        if latest is None or "sha" not in latest:
            return ""
        return latest["sha"]

    def has_known_version(self) -> bool:
        """
        Return true if the reference spec object is hard-coded with a latest
        known version.
        """
        return self.SpecVersion != ""

    def write_info(self, info: Dict[str, Dict[str, Any] | str]):
        """
        Write info about the reference specification used into the output
        fixture.
        """
        info["reference-spec"] = self.name()
        info["reference-spec-version"] = self.SpecVersion

    @staticmethod
    def parseable_from_module(module_dict: Dict[str, Any]) -> bool:
        """Check whether the module contains a git reference spec."""
        return "REFERENCE_SPEC_GIT_PATH" in module_dict

    @staticmethod
    def parse_from_module(module_dict: Dict[str, Any]) -> "ReferenceSpec":
        """Parse the module's dict into a reference spec."""
        if "REFERENCE_SPEC_GIT_PATH" not in module_dict:
            raise ParseModuleError

        spec_path = module_dict["REFERENCE_SPEC_GIT_PATH"]
        spec = GitReferenceSpec(SpecPath=spec_path)
        if "REFERENCE_SPEC_VERSION" in module_dict:
            spec.SpecVersion = module_dict["REFERENCE_SPEC_VERSION"]
        return spec


_ = GitReferenceSpec(SpecPath="")
