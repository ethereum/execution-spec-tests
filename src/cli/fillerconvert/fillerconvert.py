"""Simple CLI tool that reads filler files in the `ethereum/tests` format."""

import argparse
import json
from glob import glob
from pathlib import Path
from typing import Dict

import yaml
from pydantic import BaseModel

from .structures.state_test_filler import StateTestInFiller


def remove_comments(d: dict) -> dict:
    """Remove comments from a dictionary."""
    result = {}
    for k, v in d.items():
        if isinstance(k, str) and k.startswith("//"):
            continue
        if isinstance(v, dict):
            v = remove_comments(v)
        elif isinstance(v, list):
            v = [remove_comments(i) if isinstance(i, dict) else i for i in v]
        result[k] = v
    return result


class StateFiller(BaseModel):
    """Class that represents a state test filler."""

    tests: Dict[str, StateTestInFiller]

    @classmethod
    def from_json(cls, path: Path) -> "StateFiller":
        """Read the state filler from a JSON file."""
        with open(path, "r") as f:
            o = json.load(f)
            return StateFiller(tests=remove_comments(o))

    @classmethod
    def from_yml(cls, path: Path) -> "StateFiller":
        """Read the state filler from a YML file."""
        with open(path, "r") as f:
            o = yaml.load(f, Loader=yaml.FullLoader)
            return StateFiller(tests=remove_comments(o))


def main() -> None:
    """Run the main function."""
    parser = argparse.ArgumentParser(description="Filler parser.")

    parser.add_argument(
        "mode", type=str, help="The type of filler we are trying to parse: blockchain/state."
    )
    parser.add_argument("folder_path", type=Path, help="The path to the JSON/YML filler directory")

    args = parser.parse_args()
    folder_path = Path(str(args.folder_path).split("=")[-1])

    files = glob(str(folder_path / "**" / "*.json"), recursive=True) + glob(
        str(folder_path / "**" / "*.yml"), recursive=True
    )

    filler_cls = StateFiller
    if args.mode == "blockchain":
        raise NotImplementedError("Blockchain filler not implemented yet.")

    for file in files:
        print(file)
        if file.endswith(".json"):
            try:
                filler_cls.from_json(Path(file)).model_dump(mode="json", by_alias=True)
            except Exception as e:
                raise Exception(f"Error parsing {file}") from e
        elif file.endswith(".yml"):
            try:
                filler_cls.from_yml(Path(file)).model_dump(mode="json", by_alias=True)
            except Exception as e:
                raise Exception(f"Error parsing {file}") from e
