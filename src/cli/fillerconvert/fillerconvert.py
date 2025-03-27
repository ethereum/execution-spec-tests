"""Simple CLI tool that reads filler files in the `ethereum/tests` format."""

import argparse
from glob import glob
from pathlib import Path

from .structures.state_test_filler import StateFiller


def main() -> None:
    """Run the main function."""
    parser = argparse.ArgumentParser(description="Filler parser.")

    parser.add_argument(
        "mode", type=str, help="The type of filler we are trying to parse: blockchain/state."
    )
    parser.add_argument("folder_path", type=Path, help="The path to the JSON/YML filler directory")

    args = parser.parse_args()
    folder_path = Path(str(args.folder_path).split("=")[-1])

    print("Scanning: " + str(folder_path))
    files = glob(str(folder_path / "**" / "*.json"), recursive=True) + glob(
        str(folder_path / "**" / "*.yml"), recursive=True
    )

    filler_cls = StateFiller
    if args.mode == "blockchain":
        raise NotImplementedError("Blockchain filler not implemented yet.")

    for file in files:
        # if not file.endswith("CreateOOGafterMaxCodesizeFiller.yml"):
        #    continue
        if (
            "stExpectSection" in file  # retesteth test parser tests
            # Solidity skipped tests:
            or file.endswith("stExample/solidityExampleFiller.yml")
            or file.endswith("vmPerformance/performanceTesterFiller.yml")
            or file.endswith("vmPerformance/loopExpFiller.yml")
            or file.endswith("vmPerformance/loopMulFiller.yml")
            or file.endswith("stRevertTest/RevertRemoteSubCallStorageOOGFiller.yml")
            or file.endswith("stSolidityTest/SelfDestructFiller.yml")
        ):
            continue
        if file.endswith("Filler.json"):
            try:
                print("Process: " + file)
                filler_cls.from_json(Path(file)).model_dump(mode="json", by_alias=True)
            except Exception as e:
                raise Exception(f"Error parsing {file}") from e
        elif file.endswith("Filler.yml"):
            try:
                filler_cls.from_yml(Path(file)).model_dump(mode="json", by_alias=True)
            except Exception as e:
                raise Exception(f"Error parsing {file}") from e
