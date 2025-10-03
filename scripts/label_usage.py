#!/usr/bin/env python3
"""Check label usage in ethereum/execution-spec-tests."""

import json
import subprocess

def run_gh(args):
    """Run gh CLI command."""
    result = subprocess.run(
        ["gh"] + args, capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)

# Get all labels
labels = run_gh([
    "label", "list",
    "--repo", "ethereum/execution-spec-tests",
    "--limit", "1000",
    "--json", "name,color,description"
])

print("Counting label usage...")
usage = []

for label in labels:
    name = label["name"]

    # Count issues
    issues = run_gh([
        "issue", "list",
        "--repo", "ethereum/execution-spec-tests",
        "--label", name,
        "--limit", "1000",
        "--state", "all",
        "--json", "number"
    ])

    # Count PRs
    prs = run_gh([
        "pr", "list",
        "--repo", "ethereum/execution-spec-tests",
        "--label", name,
        "--limit", "1000",
        "--state", "all",
        "--json", "number"
    ])

    total = len(issues) + len(prs)
    usage.append((total, name))
    print(f"{name}: {total}")

# Sort by usage
usage.sort()

print("\n" + "="*80)
print("Labels with < 5 uses:")
print("="*80)
for count, name in usage:
    if count < 5:
        print(f"{count:3d} | {name}")
    else:
        break

print("\n" + "="*80)
print("All labels sorted by usage:")
print("="*80)
for count, name in usage:
    print(f"{count:3d} | {name}")
