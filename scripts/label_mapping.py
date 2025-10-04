#!/usr/bin/env python3
"""
Label migration script for ethereum/execution-spec-tests.

This script helps migrate labels to align with execution-specs conventions
and the new package structure from issue #2209.

Modes:
  1. create: Create new labels in target repo (safe, for testing)
  2. migrate: Full migration - create labels, update issues/PRs, delete old labels

Usage:
  # Test label creation in a different repo
  python scripts/label_mapping.py create --repo danceratopz/execution-specs-labels

  # Full migration (DESTRUCTIVE - use with caution)
  python scripts/label_mapping.py migrate --repo ethereum/execution-spec-tests
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class Label:
    """Represents a GitHub label."""

    name: str
    color: str
    description: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {"name": self.name, "color": self.color, "description": self.description}


# Color scheme aligned with ethereum/execution-specs
COLORS = {
    "area": "FBCA04",  # Yellow - Area labels (A-*)
    "category": "C5DEF5",  # Light Blue - Category labels (C-*)
    "experience": "02E10C",  # Bright Green - Experience/Difficulty labels (E-*, from Rust)
    "priority": "E99695",  # Pink - Priority labels (P-*)
    "fork": "D4C5F9",  # Purple - Fork labels (F-*)
    "status": "D4C5F9",  # Purple - Status labels (S-*)
}


# Label mapping configuration
# Format: "old_label_name": Label(new_name, color, description)
# Set to None to delete a label without replacement
# Set to "KEEP" to keep the label unchanged
LABEL_MAPPING: dict[str, Label | None | str] = {
    # Area: Package-level labels (A-test-*)
    "scope:base_types": Label(
        "A-test-base_types",
        COLORS["area"],
        "Area: ethereum_spec_tests/base_types package",
    ),
    "scope:types": Label(
        "A-test-types", COLORS["area"], "Area: ethereum_spec_tests/types package"
    ),
    "scope:tools": Label(
        "A-test-tools", COLORS["area"], "Area: ethereum_spec_tests/tools package"
    ),
    "scope:forks": Label(
        "A-test-forks", COLORS["area"], "Area: ethereum_spec_tests/forks package"
    ),
    "scope:pytest": Label(
        "A-test-pytest", COLORS["area"], "Area: ethereum_spec_tests/pytest package"
    ),
    "scope:exceptions": Label(
        "A-test-exceptions",
        COLORS["area"],
        "Area: ethereum_spec_tests/exceptions package",
    ),
    "scope:cli": Label(
        "A-test-client-clis",
        COLORS["area"],
        "Area: ethereum_spec_tests/client_clis package",
    ),
    "scope:tests": Label(
        "A-test-tests", COLORS["area"], "Area: EL client test cases in ./tests/"
    ),
    "scope:docs": Label("A-doc", COLORS["area"], "Area: documentation"),
    "scope:ci": Label("A-ci", COLORS["area"], "Area: continuous integration"),
    "scope:tooling": Label(
        "A-test-config", COLORS["area"], "Area: Python tooling configuration (uv, ruff, tox)"
    ),
    "scope:deps": Label(
        "A-test-deps", COLORS["area"], "Area: package dependency updates"
    ),
    "scope:packaging": Label(
        "A-test-packaging", COLORS["area"], "Area: Python packaging configuration"
    ),
    # Area: CLI sub-commands (A-test-cli-*)
    "scope:eest": Label(
        "A-test-cli-eest", COLORS["area"], "Area: ethereum_test_cli/eest command"
    ),
    "scope:make": Label(
        "A-test-cli-make", COLORS["area"], "Area: ethereum_test_cli/make command"
    ),
    "scope:gentest": Label(
        "A-test-cli-gentest", COLORS["area"], "Area: ethereum_test_cli/gentest command"
    ),
    "scope:fill": Label(
        "A-test-cli-fill", COLORS["area"], "Area: ethereum_test_cli/fill command"
    ),
    "scope:consume": Label(
        "A-test-cli-consume", COLORS["area"], "Area: ethereum_test_cli/consume command"
    ),
    "scope:execute": Label(
        "A-test-cli-execute", COLORS["area"], "Area: ethereum_test_cli/execute command"
    ),
    # Delete vague labels
    "scope:fw": None,  # Too vague - users should use specific package labels
    "scope:checklists": None,  # Package being removed/integrated
    "scope:evm": Label(
        "A-test-vm", COLORS["area"], "Area: ethereum_spec_tests/vm package"
    ),
    # Category labels (C-*)
    "type:bug": Label("C-bug", COLORS["category"], "Category: bug, deviation, or problem"),
    "type:feat": Label(
        "C-enhance", COLORS["category"], "Category: request for an improvement"
    ),
    "type:refactor": Label(
        "C-refactor", COLORS["category"], "Category: code refactoring"
    ),
    "type:test": Label(
        "C-test", COLORS["category"], "Category: framework unit tests (not EL client tests)"
    ),
    "type:chore": Label("C-chore", COLORS["category"], "Category: maintenance task"),
    "type:docs": Label(
        "C-doc", COLORS["category"], "Category: documentation improvement"
    ),
    # Fork labels (F-*)
    "fork:prague": Label("F-prague", COLORS["fork"], "Fork: Prague hardfork"),
    "fork:osaka": Label("F-osaka", COLORS["fork"], "Fork: Osaka hardfork"),
    "fork:amsterdam": Label("F-amsterdam", COLORS["fork"], "Fork: Amsterdam hardfork"),
    "fork: amsterdam": Label(
        "F-amsterdam", COLORS["fork"], "Fork: Amsterdam hardfork"
    ),  # Fix spacing
    # Status labels (S-*)
    "needs-discussion": Label(
        "S-needs-discussion", COLORS["status"], "Status: needs discussion before proceeding"
    ),
    "needs-attention": Label(
        "S-needs-attention", COLORS["status"], "Status: needs attention from maintainers"
    ),
    # Keep these unchanged (standard GitHub labels)
    "help wanted": "KEEP",
    "good first issue": Label(
        "good first issue", COLORS["experience"], "Good for newcomers"
    ),
    "tracker": "KEEP",
    "automated issue": "KEEP",
    "report": "KEEP",
    "port": "KEEP",
    "t8ntools": Label(
        "A-test-client-clis",
        COLORS["area"],
        "Area: ethereum_spec_tests/client_clis package",
    ),
    "feature:eof": Label(
        "A-test-eof", COLORS["area"], "Area: EOF (EVM Object Format) feature"
    ),
    "feature:stateless": Label(
        "A-test-benchmark", COLORS["area"], "Area: Benchmarking feature"
    ),
    "feature:zkevm": Label(
        "A-test-benchmark", COLORS["area"], "Area: Benchmarking feature"
    ),
    "feature:benchmark": Label(
        "A-test-benchmark", COLORS["area"], "Area: Benchmarking feature"
    ),
    "Finalize Weld": "KEEP",
    # Priority labels already aligned
    "P-low": "KEEP",
    "P-medium": "KEEP",
    "P-high": "KEEP",
    "P-urgent": "KEEP",
    # Delete these generic/duplicate labels
    "duplicate": None,
    "invalid": None,
    "question": Label(
        "C-question",
        COLORS["category"],
        "Category: question or request for clarification",
    ),
    "wontfix": None,
}


# New labels to create (not mapped from old ones)
NEW_LABELS: list[Label] = [
    Label(
        "A-test-ethereum_test_cli",
        COLORS["area"],
        "Area: ethereum_spec_tests/ethereum_test_cli package",
    ),
    Label(
        "A-test-execution", COLORS["area"], "Area: ethereum_spec_tests/execution package"
    ),
    Label(
        "A-test-fixtures", COLORS["area"], "Area: ethereum_spec_tests/fixtures package"
    ),
    Label("A-test-rpc", COLORS["area"], "Area: ethereum_spec_tests/rpc package"),
    Label("A-test-specs", COLORS["area"], "Area: ethereum_spec_tests/specs package"),
    # Experience labels to align with execution-specs
    Label("E-easy", COLORS["experience"], "Experience: easy, good for newcomers"),
    Label("E-medium", COLORS["experience"], "Experience: of moderate difficulty"),
    Label(
        "E-hard",
        COLORS["experience"],
        "Experience: difficult, probably not for the faint of heart",
    ),
]


def run_gh_command(args: list[str]) -> dict[str, Any] | list[dict[str, Any]] | str:
    """Run a gh CLI command and return parsed JSON output."""
    result = subprocess.run(
        ["gh"] + args, capture_output=True, text=True, check=True  # noqa: S603
    )
    if result.stdout.strip():
        return json.loads(result.stdout)
    return result.stdout


def fetch_labels(repo: str) -> list[Label]:
    """Fetch all labels from a GitHub repository."""
    print(f"Fetching labels from {repo}...")
    data = run_gh_command(
        ["label", "list", "--repo", repo, "--limit", "1000", "--json", "name,color,description"]
    )
    assert isinstance(data, list), "Expected list of labels"
    return [Label(name=label["name"], color=label["color"], description=label["description"]) for label in data]


def create_label(repo: str, label: Label, dry_run: bool = False) -> None:
    """Create a new label in the repository."""
    cmd = f"Creating label: {label.name}"
    if dry_run:
        print(f"[DRY RUN] {cmd}")
        return

    print(cmd)
    try:
        run_gh_command(
            [
                "label",
                "create",
                label.name,
                "--repo",
                repo,
                "--color",
                label.color,
                "--description",
                label.description,
            ]
        )
    except subprocess.CalledProcessError as e:
        if "already exists" in e.stderr:
            print(f"  ⚠️  Label already exists, skipping")
        else:
            raise


def delete_label(repo: str, label_name: str, dry_run: bool = False) -> None:
    """Delete a label from the repository."""
    cmd = f"Deleting label: {label_name}"
    if dry_run:
        print(f"[DRY RUN] {cmd}")
        return

    print(cmd)
    run_gh_command(["label", "delete", label_name, "--repo", repo, "--yes"])


def create_mode(repo: str, dry_run: bool = False) -> None:
    """Mode 1: Create new labels in target repo (safe mode)."""
    print(f"\n{'='*80}")
    print(f"CREATE MODE: Creating new labels in {repo}")
    print(f"{'='*80}\n")

    # Fetch existing labels
    existing_labels = fetch_labels(repo)
    existing_names = {label.name for label in existing_labels}

    # Collect all new labels to create
    labels_to_create: list[Label] = []

    # Add mapped labels
    for old_name, mapping in LABEL_MAPPING.items():
        if isinstance(mapping, Label):
            if mapping.name not in existing_names:
                labels_to_create.append(mapping)

    # Add new labels
    for label in NEW_LABELS:
        if label.name not in existing_names:
            labels_to_create.append(label)

    # Remove duplicates
    seen = set()
    unique_labels = []
    for label in labels_to_create:
        if label.name not in seen:
            seen.add(label.name)
            unique_labels.append(label)

    print(f"\nWill create {len(unique_labels)} new labels:\n")
    for label in sorted(unique_labels, key=lambda x: x.name):
        print(f"  • {label.name:40s} #{label.color} - {label.description}")

    if not dry_run:
        print("\nCreating labels...")
        for label in unique_labels:
            create_label(repo, label, dry_run=dry_run)

    print(f"\n✅ Done! Created {len(unique_labels)} labels in {repo}")


def migrate_mode(repo: str, dry_run: bool = False) -> None:
    """Mode 2: Full migration - create labels, update issues/PRs, delete old labels."""
    print(f"\n{'='*80}")
    print(f"MIGRATE MODE: Full label migration for {repo}")
    print(f"{'='*80}\n")

    if not dry_run:
        response = input("⚠️  This will modify labels on ALL issues and PRs. Continue? [y/N] ")
        if response.lower() != "y":
            print("Migration cancelled.")
            sys.exit(0)

    # Step 1: Create all new labels
    print("\n[Step 1/3] Creating new labels...")
    create_mode(repo, dry_run=dry_run)

    # Step 2: Update issues and PRs
    print("\n[Step 2/3] Updating issues and PRs...")
    # TODO: Implement issue/PR label updates

    # Step 3: Delete old labels
    print("\n[Step 3/3] Deleting old labels...")
    labels_to_delete = [
        old_name for old_name, mapping in LABEL_MAPPING.items() if mapping is None
    ]

    for label_name in labels_to_delete:
        delete_label(repo, label_name, dry_run=dry_run)

    print(f"\n✅ Migration complete for {repo}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate labels for execution-spec-tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "mode",
        choices=["create", "migrate"],
        help="Mode: 'create' (safe, create labels only) or 'migrate' (full migration)",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Target repository (e.g., 'danceratopz/execution-specs-labels')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    try:
        if args.mode == "create":
            create_mode(args.repo, dry_run=args.dry_run)
        elif args.mode == "migrate":
            migrate_mode(args.repo, dry_run=args.dry_run)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running gh command: {e}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
