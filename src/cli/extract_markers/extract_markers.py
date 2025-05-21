"""Parse given .py files to extract ported_from markers for the bash script."""

import argparse
import ast
import re
from urllib.parse import urlparse


def convert_to_filled(file_path: str) -> str | None:
    """Convert source link to filler to filled test path."""
    path = urlparse(file_path).path
    if "/src/" in path:
        path = path.split("/src/", 1)[1]

    if path.endswith((".sh", ".js")):
        return None

    # Remove "Filler" from the path components
    path = path.replace("TestsFiller", "Tests")

    # Replace file extension to .json
    path = re.sub(r"Filler\.(yml|yaml|json)$", r".json", path)

    return path


def extract_coverage_urls_from_ported_marker(file_path: str, urls: list):
    """
    Parse ported_from test marker from .py test file.
    And print filled test link instead of source.
    """
    with open(file_path, "r") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    if dec.func.attr == "ported_from":
                        if dec.args and isinstance(dec.args[0], ast.List):
                            for el in dec.args[0].elts:
                                filled_test = convert_to_filled(ast.literal_eval(el))
                                if filled_test is not None:
                                    urls.append(filled_test)


def main() -> None:
    """Extract_markers entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="One or more test .py files")
    args = parser.parse_args()
    all_files: list = []
    for path in args.files:
        extract_coverage_urls_from_ported_marker(path, all_files)
    print(" ".join(all_files))
