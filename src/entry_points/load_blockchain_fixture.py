"""
Load a blockchain test fixture json into a pydantic model.
"""

import argparse
import json
from pathlib import Path
from typing import Dict

# import rich
from pydantic import RootModel, ValidationError

from ethereum_test_tools.spec.base.base_test import HashMismatchException
from ethereum_test_tools.spec.blockchain.types import Fixture as BlockchainFixture

"""
Top-level model that holds multiple blockchain test fixtures.

The top-level keys in our JSON are dynamic and represent the test name. By
defining a RootModel, we can use the `root` attribute to access the fixtures,
but the `root` attribute is not included in the model dump.
"""
BlockchainFixtures = RootModel[Dict[str, BlockchainFixture]]


def process_directory(input_dir: Path, output_dir: Path):
    """
    Process a directory.

    Processes each .json file in the input directory and its subdirectories, and
    writes the sorted .json files to the corresponding locations in the output
    directory.

    Args:
        input_dir: The Path object of the input directory.
        output_dir: The Path object of the output directory.

    Returns:
        None.
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    for child in input_dir.iterdir():
        if child.is_dir():
            process_directory(child, output_dir / child.name)
        elif child.suffix == ".json":
            read_write_fixture(child, output_dir / child.name)


def read_write_fixture(fixture_file: Path, output_file: Path) -> None:  # noqa: D103

    try:
        with open(fixture_file, "r") as f:
            data = json.load(f)

        blockchain_fixtures = BlockchainFixtures(data)

        with open(output_file, "w") as file:
            file.write(
                blockchain_fixtures.model_dump_json(by_alias=True, exclude_none=True, indent=4)
            )

    except json.JSONDecodeError as e:
        print(f"Error reading JSON file {fixture_file}: {e}")

    except ValidationError as e:
        print(f"Validation error {fixture_file}: {e}")

    except HashMismatchException:
        print(f"Hash mismatch in {fixture_file}.")

    except Exception as e:
        print(f"Error processing {fixture_file}: {e}")
        raise e


def main() -> None:
    """
    Main function.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Load a blockchain test fixture ino a Pydantic model and write it to file.\n"
            "Example usage: "
            "python -m src.entry_points.load_blockchain_fixture fixtures/blockchain_tests/"
        )
    )
    parser.add_argument("fixture_json", type=Path, help="The path to a directory containing JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/out"),
        help="The output directory to write JSON.",
    )
    args = parser.parse_args()

    process_directory(args.fixture_json, args.output)


if __name__ == "__main__":
    main()
