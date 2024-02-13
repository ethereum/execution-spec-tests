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
from pathlib import Path


def get_fixture_hash_map(fixtures_directory: str) -> dict:
    """
    Generates a sha256 hash map of the fixture json files, mapped to the file name.
    The hash for each fixture is calculated without the `_info` key.
    """
    hash_map = {}
    fixtures_dir_path = Path(fixtures_directory)
    for fixture_path in fixtures_dir_path.rglob("*.json"):
        with open(fixture_path, "r") as file:
            data = json.load(file)
            data.pop("_info", None)
            fixture_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        relative_path_parts = fixture_path.relative_to(fixtures_dir_path).parts
        modified_path = Path(*relative_path_parts[1:]).as_posix()
        hash_map[modified_path] = [fixture_hash]
    return hash_map


def get_fixture_cumulative_hash(fixtures_hash_map: dict) -> str:
    """
    Creates a sha256 hash of the sorted hashes of the fixture json files.
    """
    sorted_hashes = sorted(fixtures_hash_map.keys())
    cumulative_hash = hashlib.sha256("".join(sorted_hashes).encode()).hexdigest()
    return cumulative_hash


def generate_fixture_hash_map_dict(cumulative_hash: str, hash_map: dict) -> dict:
    """
    Generates a dict containing both the hash map of fixture files and the cumulative hash.
    """
    return {"cumulative_hash": cumulative_hash, "hash_map": hash_map}


def generate_fixture_hash_map_json(
    fixtures_directory: str, fixture_hash_map_json: str = "fixture_hash_map.json"
) -> None:
    """
    Generates a json file containing the hash map of fixture files and the cumulative hash,
    directly from the input fixtures directory. Used within CI/CD artifact generation.
    """
    hash_map = get_fixture_hash_map(fixtures_directory)
    cumulative_hash = get_fixture_cumulative_hash(hash_map)
    with open(fixture_hash_map_json, "w") as file:
        json.dump(generate_fixture_hash_map_dict(cumulative_hash, hash_map), file, indent=4)


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
        default=None,
        help="The commit hash to compare the input fixtures against.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists() or not input_path.is_dir():
        raise FileNotFoundError(
            f"Error: The input or default fixtures directory does not exist: {args.input}"
        )

    # Todo - implement the fixture diff comparison locally
    # Currently using dfx for testing the json generation
    generate_fixture_hash_map_json(args.input)


if __name__ == "__main__":
    main()
