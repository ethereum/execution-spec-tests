#!/usr/bin/env python3
"""Generate HTML visualization of label mappings with usage counts."""

import json
import subprocess
from label_mapping import LABEL_MAPPING, NEW_LABELS, Label


def run_gh(args):
    """Run gh CLI command."""
    result = subprocess.run(
        ["gh"] + args, capture_output=True, text=True, check=True  # noqa: S603
    )
    return json.loads(result.stdout) if result.stdout.strip() else []


def get_label_usage(repo: str, label_name: str) -> tuple[int, int]:
    """Get issue and PR count for a label."""
    issues = run_gh([
        "issue", "list",
        "--repo", repo,
        "--label", label_name,
        "--limit", "1000",
        "--state", "all",
        "--json", "number"
    ])
    prs = run_gh([
        "pr", "list",
        "--repo", repo,
        "--label", label_name,
        "--limit", "1000",
        "--state", "all",
        "--json", "number"
    ])
    return len(issues), len(prs)


def get_existing_label_color(repo: str, label_name: str) -> str:
    """Get the color of an existing label."""
    labels = run_gh([
        "label", "list",
        "--repo", repo,
        "--limit", "1000",
        "--json", "name,color"
    ])
    for label in labels:
        if label["name"] == label_name:
            return label["color"]
    return "808080"


def generate_html():
    """Generate HTML visualization."""
    repo = "ethereum/execution-spec-tests"

    print("Fetching label usage data...")

    html = """<!DOCTYPE html>
<html>
<head>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; padding: 20px; }
table { border-collapse: collapse; width: 100%; margin-top: 20px; }
th, td { padding: 8px 12px; text-align: left; border: 1px solid #ddd; }
th { background-color: #f6f8fa; font-weight: 600; }
.label {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid rgba(27,31,36,0.15);
}
.arrow { color: #666; font-weight: bold; }
.usage { color: #666; font-size: 12px; }
.delete { color: #d73a4a; font-style: italic; }
.keep { color: #28a745; font-style: italic; }
.new-label { background-color: #fffbdd; }
h1 { color: #24292f; }
h2 { color: #24292f; margin-top: 30px; border-bottom: 1px solid #d0d7de; padding-bottom: 8px; }
.summary { background: #f6f8fa; padding: 15px; border-radius: 6px; margin: 20px 0; }
</style>
</head>
<body>
<h1>Label Migration Mapping</h1>
<p>This document shows the mapping from old labels to new labels for <code>ethereum/execution-spec-tests</code>.</p>

<div class="summary">
<strong>Summary:</strong>
<ul>
<li>Following <a href="https://forge.rust-lang.org/release/issue-triaging.html">Rust project label conventions</a></li>
<li>Labels grouped by prefix with consistent colors</li>
<li>At most one label from each group per issue/PR (flexible for multi-area issues)</li>
</ul>
</div>

<h2>Label Groups</h2>
<ul>
<li><strong>A-*</strong> (Area) - <span class="label" style="background-color: #FBCA04; color: #000;">Yellow #FBCA04</span> - Package and area labels</li>
<li><strong>C-*</strong> (Category) - <span class="label" style="background-color: #C5DEF5; color: #000;">Light Blue #C5DEF5</span> - Issue/PR categories</li>
<li><strong>E-*</strong> (Experience) - <span class="label" style="background-color: #02E10C; color: #000;">Green #02E10C</span> - Difficulty level (from Rust)</li>
<li><strong>F-*</strong> (Fork) - <span class="label" style="background-color: #D4C5F9; color: #000;">Purple #D4C5F9</span> - Ethereum fork labels</li>
<li><strong>P-*</strong> (Priority) - <span class="label" style="background-color: #E99695; color: #000;">Pink #E99695</span> - Priority levels</li>
<li><strong>S-*</strong> (Status) - <span class="label" style="background-color: #D4C5F9; color: #000;">Purple #D4C5F9</span> - Status labels</li>
</ul>

<h2>Mappings</h2>
<table>
<thead>
<tr>
<th>Old Label</th>
<th></th>
<th>New Label</th>
<th>Usage (Issues/PRs)</th>
</tr>
</thead>
<tbody>
"""

    # Collect all mappings with usage data
    mappings = []

    for old_name, mapping in LABEL_MAPPING.items():
        print(f"Processing: {old_name}")

        if mapping == "KEEP":
            continue

        old_color = get_existing_label_color(repo, old_name)
        issue_count, pr_count = get_label_usage(repo, old_name)
        total = issue_count + pr_count

        if isinstance(mapping, Label):
            mappings.append({
                "old_name": old_name,
                "old_color": old_color,
                "new_name": mapping.name,
                "new_color": mapping.color,
                "description": mapping.description,
                "issues": issue_count,
                "prs": pr_count,
                "total": total,
                "action": "map"
            })
        elif mapping is None:
            mappings.append({
                "old_name": old_name,
                "old_color": old_color,
                "new_name": "DELETE",
                "new_color": "d73a4a",
                "description": "Will be deleted",
                "issues": issue_count,
                "prs": pr_count,
                "total": total,
                "action": "delete"
            })

    # Sort by total usage (descending)
    mappings.sort(key=lambda x: x["total"], reverse=True)

    # Add rows
    for m in mappings:
        old_fg = "#000" if int(m["old_color"], 16) > 0x808080 else "#fff"
        new_fg = "#000" if int(m["new_color"], 16) > 0x808080 else "#fff"

        if m["action"] == "delete":
            html += f"""<tr>
<td><span class="label" style="background-color: #{m['old_color']}; color: {old_fg};">{m['old_name']}</span></td>
<td class="arrow">→</td>
<td><span class="delete">DELETE</span></td>
<td class="usage">{m['issues']} issues, {m['prs']} PRs</td>
</tr>
"""
        else:
            html += f"""<tr>
<td><span class="label" style="background-color: #{m['old_color']}; color: {old_fg};">{m['old_name']}</span></td>
<td class="arrow">→</td>
<td><span class="label" style="background-color: #{m['new_color']}; color: {new_fg};">{m['new_name']}</span></td>
<td class="usage">{m['issues']} issues, {m['prs']} PRs</td>
</tr>
"""

    # Add new labels section
    html += """</tbody>
</table>

<h2>New Labels (No Old Label)</h2>
<table>
<thead>
<tr>
<th>Label</th>
<th>Description</th>
</tr>
</thead>
<tbody>
"""

    for label in sorted(NEW_LABELS, key=lambda x: x.name):
        fg = "#000" if int(label.color, 16) > 0x808080 else "#fff"
        html += f"""<tr class="new-label">
<td><span class="label" style="background-color: #{label.color}; color: {fg};">{label.name}</span></td>
<td>{label.description}</td>
</tr>
"""

    html += """</tbody>
</table>

<h2>Labels Kept As-Is</h2>
<ul>
"""

    for old_name, mapping in LABEL_MAPPING.items():
        if mapping == "KEEP":
            html += f"<li><code>{old_name}</code></li>\n"

    html += """</ul>

</body>
</html>
"""

    with open("mapping.html", "w") as f:
        f.write(html)

    print("\n✅ Generated mapping.html")


if __name__ == "__main__":
    generate_html()
