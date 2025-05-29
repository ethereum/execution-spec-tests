"""
Pytest plugin for generating EIP test completion checklists.

This plugin collects checklist markers from tests and generates a filled checklist
for each EIP based on the template at
docs/writing_tests/checklist_templates/eip_testing_checklist_template.md
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pytest

from .gen_test_doc.page_props import EipChecklistPageProps

logger = logging.getLogger("mkdocs")


def pytest_addoption(parser: pytest.Parser):
    """Add command-line options for checklist generation."""
    group = parser.getgroup("checklist", "EIP checklist generation options")
    group.addoption(
        "--checklist-output",
        action="store",
        dest="checklist_output",
        type=Path,
        default=Path("./checklists"),
        help="Directory to output the generated checklists",
    )
    group.addoption(
        "--checklist-eip",
        action="append",
        dest="checklist_eips",
        type=int,
        default=[],
        help="Generate checklist only for specific EIP(s)",
    )
    group.addoption(
        "--checklist-doc-gen",
        action="store_true",
        dest="checklist_doc_gen",
        default=False,
        help="Generate checklists for documentation (uses mkdocs_gen_files)",
    )


TITLE_LINE = "# EIP Execution Layer Testing Checklist Template"
PERCENTAGE_LINE = "| TOTAL_CHECKLIST_ITEMS | COVERED_CHECKLIST_ITEMS | PERCENTAGE |"


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):  # noqa: D103
    config.pluginmanager.register(EIPChecklistCollector(), "eip-checklist-collector")


@dataclass
class EIPItem:
    """Represents an EIP checklist item."""

    id: str
    description: str
    tests: List[str]
    covered: bool = False

    @classmethod
    def from_checklist_line(cls, line: str) -> "EIPItem | None":
        """Create an EIP item from a checklist line."""
        match = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|", line)
        if not match:
            return None
        return cls(id=match.group(1), description=match.group(2), tests=[], covered=False)

    def with_tests(self, tests: List[str]) -> "EIPItem":
        """Return a new EIP item with the given tests."""
        new_tests = sorted(set(self.tests + tests))
        return EIPItem(
            id=self.id,
            description=self.description,
            tests=new_tests,
            covered=len(new_tests) > 0,
        )

    def __str__(self) -> str:
        """Return a string representation of the EIP item."""
        return (
            f"| `{self.id}` "
            f"| {self.description} "
            f"| {'✅' if self.covered else ' '} "
            f"| {', '.join(self.tests)} "
            "|"
        )


class EIPChecklistCollector:
    """Collects and manages EIP checklist items from test markers."""

    def __init__(self: "EIPChecklistCollector"):
        """Initialize the EIP checklist collector."""
        self.eip_checklist_items: Dict[int, Dict[str, Set[Tuple[str, str]]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self.template_path = (
            Path(__file__).parents[3]
            / "docs"
            / "writing_tests"
            / "checklist_templates"
            / "eip_testing_checklist_template.md"
        )
        self.eip_paths: Dict[int, Path] = {}

        if not self.template_path.exists():
            pytest.fail(f"EIP checklist template not found at {self.template_path}")

        self.template_content = self.template_path.read_text()
        self.template_items: Dict[str, Tuple[EIPItem, int]] = {}  # ID -> (item, line_number)
        self.all_ids: Set[str] = set()

        # Parse the template to extract checklist item IDs and descriptions
        lines = self.template_content.splitlines()
        for i, line in enumerate(lines):
            # Match lines that contain checklist items with IDs in backticks
            item = EIPItem.from_checklist_line(line)
            if item:
                self.template_items[item.id] = (item, i + 1)
                self.all_ids.add(item.id)

    def extract_eip_from_path(self, test_path: Path) -> Tuple[Optional[int], Optional[Path]]:
        """Extract EIP number from test file path."""
        # Look for patterns like eip1234_ or eip1234/ in the path
        for part_idx, part in enumerate(test_path.parts):
            match = re.match(r"eip(\d+)", part)
            if match:
                eip = int(match.group(1))
                eip_path = test_path.parents[len(test_path.parents) - part_idx - 2]
                return eip, eip_path
        return None, None

    def collect_from_item(self, item: pytest.Item, primary_eip: Optional[int]) -> None:
        """Collect checklist markers from a test item."""
        for marker in item.iter_markers("eip_checklist"):
            if not marker.args:
                pytest.fail(
                    f"eip_checklist marker on {item.nodeid} must have at least one argument "
                    "(item_id)"
                )
            additional_eips = marker.kwargs.get("eip", [])
            if not isinstance(additional_eips, list):
                additional_eips = [additional_eips]

            # Get the primary EIP from the test path
            if primary_eip is None:
                if not additional_eips:
                    pytest.fail(
                        f"Could not extract EIP number from test path: {item.path}. "
                        "Marker 'eip_checklist' can only be used in tests that are located in a "
                        "directory named after the EIP number, or with the eip keyword argument."
                    )
                eips = additional_eips
            else:
                eips = [primary_eip] + additional_eips

            if any(not isinstance(eip, int) for eip in eips):
                pytest.fail(
                    "EIP numbers must be integers. Found non-integer EIPs in "
                    f"{item.nodeid}: {eips}"
                )

            for item_id in marker.args:
                if item_id not in self.all_ids:
                    # TODO: If we decide to do the starts-with matching, we have to change this.
                    logger.warning(
                        f"Item ID {item_id} not found in the checklist template, "
                        f"for test {item.nodeid}"
                    )
                    continue
                for eip in eips:
                    self.eip_checklist_items[eip][item_id].add((item.nodeid, item.name))

    def generate_filled_checklist_lines(self, eip: int) -> List[str]:
        """Generate the filled checklist lines for a specific EIP."""
        # Get all checklist items for this EIP
        eip_items = self.eip_checklist_items.get(eip, {})

        # Create a copy of the template content
        filled_content = self.template_content
        lines = filled_content.splitlines()

        # Process each line in reverse order to avoid index shifting
        total_items = len(self.template_items)
        covered_items = 0
        for item_id, (checklist_item, line_num) in sorted(
            self.template_items.items(), key=lambda x: x[1][1], reverse=True
        ):
            if item_id in eip_items:
                # Find the line with this item ID
                line_idx = line_num - 1
                checklist_item = checklist_item.with_tests(
                    [f"`{test_node_id}`" for test_node_id, _ in eip_items[item_id]]
                )
                lines[line_idx] = str(checklist_item)
                covered_items += 1

        percentage = covered_items / total_items * 100
        completness_emoji = "🟢" if percentage == 100 else "🟡" if percentage > 50 else "🔴"
        lines[lines.index(PERCENTAGE_LINE)] = (
            f"| {total_items} | {covered_items} | {completness_emoji} {percentage:.2f}% |"
        )

        # Replace the title line with the EIP number
        lines[lines.index(TITLE_LINE)] = f"# EIP-{eip} Test Checklist"

        return lines

    def generate_filled_checklist(self, eip: int, output_dir: Path) -> Path:
        """Generate a filled checklist for a specific EIP."""
        lines = self.generate_filled_checklist_lines(eip)

        output_dir = output_dir / f"eip{eip}_checklist.md"

        # Write the filled checklist
        output_dir.parent.mkdir(exist_ok=True, parents=True)
        output_dir.write_text("\n".join(lines))

        return output_dir

    def pytest_collection_modifyitems(self, config: pytest.Config, items: List[pytest.Item]):
        """Collect checklist markers during test collection."""
        for item in items:
            eip, eip_path = self.extract_eip_from_path(Path(item.location[0]))
            if eip_path is not None and eip is not None:
                self.eip_paths[eip] = eip_path
            if item.get_closest_marker("derived_test"):
                continue
            self.collect_from_item(item, eip)

        if not self.eip_checklist_items:
            return

        # Check which mode we are in
        checklist_doc_gen = config.getoption("checklist_doc_gen", False)
        checklist_output = config.getoption("checklist_output", Path("checklists"))
        checklist_eips = config.getoption("checklist_eips", [])

        checklist_props = {}

        # Generate a checklist for each EIP
        for eip in sorted(self.eip_checklist_items.keys()):
            # Skip if specific EIPs were requested and this isn't one of them
            if checklist_eips and eip not in checklist_eips:
                continue

            if checklist_doc_gen:
                eip_path = self.eip_paths[eip]
                checklist_props[eip_path / "checklist.md"] = EipChecklistPageProps(
                    title=f"EIP-{eip} Test Checklist",
                    source_code_url="",
                    target_or_valid_fork="mainnet",
                    path=eip_path / "checklist.md",
                    pytest_node_id="",
                    package_name="eip_checklist",
                    eip=eip,
                    lines=self.generate_filled_checklist_lines(eip),
                )
            else:
                checklist_path = self.generate_filled_checklist(eip, checklist_output)
                print(f"Generated EIP-{eip} checklist: {checklist_path}")

        if checklist_doc_gen:
            config.checklist_props = checklist_props  # type: ignore
