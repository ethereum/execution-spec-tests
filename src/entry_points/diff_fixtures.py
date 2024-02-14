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
from typing import Dict, List, Tuple


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


def generate_fixture_tree_json(fixtures_directory: Path, output_file: str, parent_path="") -> None:
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

        for item in directory.iterdir():
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

    generate_fixture_tree_json(fixtures_directory=input_path, output_file="fixtures_tree.json")


if __name__ == "__main__":
    main()
