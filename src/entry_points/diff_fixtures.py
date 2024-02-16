"""
Functions and CLI interface for identifying differences in fixture content based on SHA256 hashes.

Features include generating SHA256 hash maps for fixture files, excluding the '_info' key for
consistency, and calculating a cumulative hash across all files for quick detection of any changes.

The CLI interface allows users to detect changes locally during development.

Example CLI Usage:
    ```
    python diff_fixtures.py --input ./fixtures --develop
    # or via CLI entry point after package installation
    dfx --input ./fixtures
    ```

CI/CD utilizes the functions to create a json fixture hash map file for the main branch during the
fixture artifact build process, and within the PR branch that a user is developing on. These are
then compared within the PR workflow during each commit to flag any changes in the fixture files.
"""

import argparse
import hashlib
import json
import os
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from dotenv import load_dotenv


def compute_fixture_hash(fixture_path: Path) -> str:
    """
    Generates a sha256 hash of a fixture json files.
    The hash for each fixture is calculated without the `_info` key.
    """
    with open(fixture_path, "r") as file:
        data = json.load(file)
        data.pop("_info", None)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def compute_cumulative_hash(hashes: List[str]) -> str:
    """
    Creates cumulative sha256 hash from a list of hashes.
    """
    return hashlib.sha256("".join(sorted(hashes)).encode()).hexdigest()


def generate_fixtures_tree_json(
    fixtures_directory: Path,
    output_file: str,
    parent_path="",
) -> None:
    """
    Generates a JSON file containing a tree structure of the fixtures directory calculating
    cumulative hashes at each folder and file. The tree structure is a nested dictionary used to
    compare fixture differences, using the cumulative hash as a quick comparison metric.
    """

    def build_tree(directory: Path, parent_path) -> Tuple[Dict, List[str]]:
        """
        Recursively builds a tree structure for fixture directories and files,
        calculating cumulative hashes at each sub tree.
        """
        directory_contents = {}
        all_hashes = []

        sorted_items = sorted(directory.iterdir(), key=lambda x: x.name)
        for item in sorted_items:
            relative_path = f"{parent_path}/{item.name}" if parent_path else item.name

            if item.is_dir():
                sub_tree, sub_tree_hashes = build_tree(item, relative_path)
                directory_contents[item.name] = [
                    {
                        "path": relative_path,
                        "hash": compute_cumulative_hash(sub_tree_hashes),
                        "contents": sub_tree,
                    }
                ]
                all_hashes.extend(sub_tree_hashes)
            elif item.suffix == ".json":
                file_hash = compute_fixture_hash(item)
                directory_contents[item.name] = [
                    {
                        "path": relative_path,
                        "hash": file_hash,
                    }
                ]
                all_hashes.append(file_hash)
        return directory_contents, all_hashes

    tree_contents, tree_hashes = build_tree(fixtures_directory, parent_path)
    fixtures_tree = {
        "fixtures": {
            "cumulative_hash": compute_cumulative_hash(tree_hashes),
            "contents": tree_contents,
        }
    }
    with open(output_file, "w") as file:
        json.dump(fixtures_tree, file, indent=4)


def write_artifact_fixtures_tree_json(commit: str = "", develop: bool = False):
    """
    Retrieves a fixtures tree artifact json data from EEST. By default, it will download the latest
    main branch base artifact. If the develop flag is set, it will download the latest development
    artifact. The commit flag can be used to download a specific artifact on the main branch based.
    """
    load_dotenv()
    github_token = os.getenv("GITHUB_PAT")
    if not github_token:
        raise ValueError("GitHub PAT not found. Ensure GITHUB_PAT is set within your .env file.")

    api_url = "https://api.github.com/repos/spencer-tb/execution-spec-tests/actions/artifacts"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    artifacts = response.json().get("artifacts", [])
    artifact_name = "fixtures_develop_hash_tree" if develop else "fixtures_hash_tree"

    for artifact in artifacts:
        artifact_commit = artifact["workflow_run"]["head_sha"]
        if (
            artifact["name"] == artifact_name  # base or develop
            and not artifact["expired"]
            and (commit == "" or artifact_commit.startswith(commit))  # latest or specific
        ):
            download_url = artifact["archive_download_url"]
            response = requests.get(download_url, headers=headers)
            response.raise_for_status()
            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                json_file_info = next(
                    (
                        file_info
                        for file_info in zip_ref.infolist()
                        if file_info.filename.endswith("_hash_tree.json")
                    ),
                    None,
                )
                if json_file_info is None:
                    raise FileNotFoundError("No fixtures tree hash file found in the artifact.")
                with zip_ref.open(json_file_info) as json_file:
                    json_data = json.load(json_file)
                    with open(f"./{artifact_name}_artifact.json", "w") as file:
                        json.dump(json_data, file, indent=4)
                return
        else:
            raise ValueError(
                f"No active artifact named {artifact_name} found or matching commit {commit}."
            )


def main():
    """
    CLI interface for comparing fixture differences between the input directory and the main
    branch fixture artifacts.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Determines if a diff exists between an input fixtures directory and the most recent "
            "built fixtures from the main branch git workflow. "
            "Does not provide detailed file changes. "
            "If no input directory is provided, `./fixtures` is used as the default. "
            "Compares only the non-development fixtures by default."
        )
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./fixtures",
        help="Input path for the fixtures directory",
    )
    parser.add_argument(
        "--develop",
        action="store_true",
        default=False,
        help="Compares all fixtures including the development fixtures.",
    )
    parser.add_argument(  # To be implemented
        "--commit",
        type=str,
        default="",
        help="The commit hash to compare the input fixtures against.",
    )
    parser.add_argument(
        "--generate-fixtures-tree-only",
        action="store_true",
        default=False,
        help=(
            "Generates a fixtures tree json file without comparing to the main branch."
            "Used mostly within the CI/CD pipeline."
        ),
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists() or not input_path.is_dir():
        raise FileNotFoundError(
            f"Error: The input or default fixtures directory does not exist: {args.input}"
        )

    if args.generate_fixtures_tree_only:
        generate_fixtures_tree_json(
            fixtures_directory=input_path, output_file="fixtures_tree.json"
        )
        return

    # Download the latest fixtures tree hash json artifact from the main branch
    write_artifact_fixtures_tree_json(commit=args.commit, develop=args.develop)

    # Generate the fixtures tree hash from the local input directory
    generate_fixtures_tree_json(
        fixtures_directory=input_path, output_file="fixtures_hash_tree_local.json"
    )


if __name__ == "__main__":
    main()
