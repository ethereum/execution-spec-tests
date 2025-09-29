#!/usr/bin/env python3
"""Transfer GitHub issues from one repository to another using the GitHub CLI."""

import argparse
import json
import re
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


# Configuration
SOURCE_REPO = "kclowes/transfer-issues-from"
TARGET_REPO = "kclowes/transfer-issues-to"

# Label translation mapping
LABEL_MAP = {
    "custom": "to-custom",
}


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    result = subprocess.run(cmd, capture_output=capture_output, text=True, shell=False)
    return result.returncode, result.stdout, result.stderr


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    # Check if gh is installed
    exit_code, _, _ = run_command(["which", "gh"])
    if exit_code != 0:
        print("Error: GitHub CLI (gh) is not installed")
        print("Install it from: https://cli.github.com/")
        return False

    # Check if authenticated
    exit_code, _, _ = run_command(["gh", "auth", "status"])
    if exit_code != 0:
        print("Error: Not authenticated with GitHub")
        print("Run: gh auth login")
        return False

    return True


def translate_label(label: str) -> str:
    """Translate a label according to the mapping."""
    label_lower = label.lower()

    # Check for exact match first (case-insensitive)
    for old_label, new_label in LABEL_MAP.items():
        if label_lower == old_label.lower():
            return new_label

    # Check for prefix match (for "custom label" -> "to-custom")
    for old_label, new_label in LABEL_MAP.items():
        if label_lower.startswith(old_label.lower()):
            return new_label

    return label


def translate_labels(labels: List[str]) -> List[str]:
    """Translate a list of labels."""
    return [translate_label(label) for label in labels]


def fetch_issues(repo: str, limit: Optional[int] = None) -> List[Dict]:
    """Fetch open issues from a repository."""
    print(f"Fetching open issues from {repo}...")

    cmd = [
        "gh",
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        "open",
        "--json",
        "number,title,body,labels,assignees,milestone",
    ]

    if limit:
        cmd.extend(["--limit", str(limit)])
    else:
        cmd.extend(["--limit", "1000"])

    exit_code, stdout, stderr = run_command(cmd)

    if exit_code != 0:
        print(f"Error fetching issues: {stderr}")
        return []

    try:
        issues = json.loads(stdout)
        return issues
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []


def transfer_issue(issue_number: int, target_repo: str, source_repo: str) -> Tuple[bool, str]:
    """Transfer an issue to the target repository using gh issue transfer."""
    cmd = [
        "gh",
        "issue",
        "transfer",
        str(issue_number),
        target_repo,
        "--repo",
        source_repo,
    ]

    exit_code, stdout, stderr = run_command(cmd)

    if exit_code != 0:
        return False, stderr

    return True, stdout.strip()


def get_repo_labels(repo: str) -> List[str]:
    """Fetch all available labels from a repository."""
    cmd = [
        "gh",
        "label",
        "list",
        "--repo",
        repo,
        "--json",
        "name",
        "--limit",
        "1000",
    ]

    exit_code, stdout, stderr = run_command(cmd)

    if exit_code != 0:
        print(f"Error fetching labels from {repo}: {stderr}")
        return []

    try:
        label_data = json.loads(stdout)
        return [label["name"] for label in label_data]
    except json.JSONDecodeError as e:
        print(f"Error parsing label JSON: {e}")
        return []


def validate_labels(labels: List[str], repo: str, available_labels: List[str]) -> bool:
    """Validate that all labels exist in the target repository."""
    if not labels:
        return True

    missing_labels = [label for label in labels if label not in available_labels]

    if missing_labels:
        print(f"  ✗ Error: The following labels do not exist in {repo}:")
        for label in missing_labels:
            print(f"    - {label}")
        print(f"  Create these labels in {repo} first, or update LABEL_MAP to translate them")
        return False

    return True


def update_issue_labels(issue_url: str, labels: List[str]) -> bool:
    """Update labels on a transferred issue."""
    if not labels:
        return True

    cmd = [
        "gh",
        "issue",
        "edit",
        issue_url,
        "--add-label",
        ",".join(labels),
    ]

    exit_code, _, stderr = run_command(cmd)
    if exit_code != 0:
        print(f"  Error updating labels: {stderr}")
    return exit_code == 0


def extract_subissue_references(body: str, repo: str) -> List[int]:
    """Extract subissue references from issue body.

    Looks for patterns like:
    - #123
    - https://github.com/owner/repo/issues/123
    - [ ] #123 (task list format)
    """
    subissues = []

    # Pattern for issue references in the same repo
    issue_ref_pattern = r'#(\d+)'
    for match in re.finditer(issue_ref_pattern, body):
        issue_num = int(match.group(1))
        if issue_num not in subissues:
            subissues.append(issue_num)

    # Pattern for full GitHub URLs
    url_pattern = rf'https://github\.com/{re.escape(repo)}/issues/(\d+)'
    for match in re.finditer(url_pattern, body):
        issue_num = int(match.group(1))
        if issue_num not in subissues:
            subissues.append(issue_num)

    return subissues


def fetch_issue_by_number(repo: str, issue_number: int) -> Optional[Dict]:
    """Fetch a specific issue by its number."""
    cmd = [
        "gh",
        "issue",
        "view",
        str(issue_number),
        "--repo",
        repo,
        "--json",
        "number,title,body,labels,assignees,milestone,state",
    ]

    exit_code, stdout, stderr = run_command(cmd)

    if exit_code != 0:
        print(f"    Warning: Could not fetch issue #{issue_number}: {stderr}")
        return None

    try:
        issue = json.loads(stdout)
        return issue
    except json.JSONDecodeError:
        return None


def transfer_issues(dry_run: bool = False, limit: Optional[int] = None, include_subissues: bool = True) -> None:
    """Transfer issues from source to target repository."""
    print("=" * 40)
    print("GitHub Issue Transfer Script")
    print(f"Source: {SOURCE_REPO}")
    print(f"Target: {TARGET_REPO}")
    print(f"Dry Run: {dry_run}")
    print(f"Include Subissues: {include_subissues}")
    if limit:
        print(f"Limit: {limit} issues")
    print("=" * 40)
    print()

    # Check prerequisites
    if not check_gh_cli():
        sys.exit(1)

    # Fetch available labels from target repository
    print(f"Fetching available labels from {TARGET_REPO}...")
    target_labels = get_repo_labels(TARGET_REPO)
    if not target_labels:
        print(f"Warning: Could not fetch labels from {TARGET_REPO}")
        print("Label validation will be skipped")
    else:
        print(f"Found {len(target_labels)} labels in target repository")
    print()

    # Fetch issues
    issues = fetch_issues(SOURCE_REPO, limit)
    print(f"Found {len(issues)} open issues")

    # Track processed issues to avoid duplicates
    processed_issues = set()
    issues_to_process = []
    parent_child_map = {}  # Track which issues are subissues of others

    # First pass: collect main issues and their subissues
    for issue in issues:
        if issue["number"] not in processed_issues:
            issues_to_process.append(issue)
            processed_issues.add(issue["number"])

            # Check for subissues if enabled
            if include_subissues and issue.get("body"):
                subissue_refs = extract_subissue_references(issue["body"], SOURCE_REPO)
                if subissue_refs:
                    print(f"  Issue #{issue['number']} references subissues: {subissue_refs}")
                    for sub_num in subissue_refs:
                        # Track parent-child relationship
                        if sub_num not in parent_child_map:
                            parent_child_map[sub_num] = []
                        parent_child_map[sub_num].append(issue["number"])

                        if sub_num not in processed_issues:
                            subissue = fetch_issue_by_number(SOURCE_REPO, sub_num)
                            if subissue and subissue.get("state") == "OPEN":
                                issues_to_process.append(subissue)
                                processed_issues.add(sub_num)
                                print(f"    Added subissue #{sub_num} to transfer queue")

    # Sort issues so subissues are processed before their parents
    # This ensures GitHub can maintain issue reference updates automatically
    def get_issue_depth(issue_num, visited=None):
        if visited is None:
            visited = set()
        if issue_num in visited:
            return 0
        visited.add(issue_num)
        if issue_num not in parent_child_map:
            return 0
        return 1 + max(get_issue_depth(parent, visited) for parent in parent_child_map[issue_num])

    issues_to_process.sort(key=lambda x: get_issue_depth(x["number"]))

    print(f"\nTotal issues to transfer (including subissues): {len(issues_to_process)}")
    print()

    if not issues_to_process:
        print("No issues to transfer")
        return

    transferred = 0
    failed = 0

    for issue in issues_to_process:
        number = issue["number"]
        title = issue["title"]

        # Extract labels
        labels = [label["name"] for label in issue.get("labels", [])]

        print("-" * 40)
        print(f"Processing Issue #{number}: {title}")

        # Translate labels if needed
        translated_labels = []
        if labels:
            translated_labels = translate_labels(labels)
            if translated_labels != labels:
                print(
                    f"  Translating labels: {', '.join(labels)} -> {', '.join(translated_labels)}"
                )

        # Validate labels exist in target repository
        if target_labels and translated_labels:
            if not validate_labels(translated_labels, TARGET_REPO, target_labels):
                print(f"  Skipping issue #{number} due to missing labels")
                failed += 1
                continue

        if dry_run:
            print("  [DRY RUN] Would transfer issue:")
            print(f"    Title: {title}")
            if labels:
                print(f"    Labels: {', '.join(labels)}")
            if translated_labels != labels:
                print(f"    Translated labels: {', '.join(translated_labels)}")

            # Validate labels in dry run too
            if target_labels and translated_labels:
                validate_labels(translated_labels, TARGET_REPO, target_labels)

            # Show if this issue references other issues
            body = issue.get("body", "")
            if body:
                subissue_refs = extract_subissue_references(body, SOURCE_REPO)
                if subissue_refs:
                    print(f"    References issues: {subissue_refs}")

            print(f"    Original: https://github.com/{SOURCE_REPO}/issues/{number}")
        else:
            print(f"  Transferring issue to {TARGET_REPO}...")

            success, result = transfer_issue(number, TARGET_REPO, SOURCE_REPO)

            if success:
                new_issue_url = result
                print(f"  ✓ Transferred: {new_issue_url}")

                # Update labels if translation is needed
                if translated_labels != labels:
                    print(f"  Updating labels...")
                    if update_issue_labels(new_issue_url, translated_labels):
                        print(f"  ✓ Updated labels")
                    else:
                        print(f"  ⚠ Failed to update labels")

                transferred += 1
            else:
                print(f"  ✗ Failed to transfer issue: {result}")
                failed += 1

    print()
    print("=" * 40)
    if dry_run:
        print("DRY RUN COMPLETE")
        print(f"Would transfer {len(issues_to_process)} issues")
        print("Run without --dry-run to actually transfer")
    else:
        print("TRANSFER COMPLETE")
        print(f"Successfully transferred: {transferred}")
        print(f"Failed: {failed}")
    print("=" * 40)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Transfer GitHub issues from one repository to another"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be transferred without actually doing it",
    )
    parser.add_argument(
        "--limit", type=int, metavar="N", help="Only transfer the first N issues"
    )
    parser.add_argument(
        "--no-subissues",
        action="store_true",
        help="Don't automatically include referenced subissues",
    )

    args = parser.parse_args()

    try:
        transfer_issues(
            dry_run=args.dry_run,
            limit=args.limit,
            include_subissues=not args.no_subissues
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
