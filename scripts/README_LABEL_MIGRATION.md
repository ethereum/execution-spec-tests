# Label Migration Scripts

This directory contains scripts for migrating GitHub labels to align with Rust project conventions and the new package structure from [issue #2209](https://github.com/ethereum/execution-spec-tests/issues/2209).

## 🎯 Goals

1. **Align with Rust conventions**: Follow [Rust's label triaging guidelines](https://forge.rust-lang.org/release/issue-triaging.html)
2. **Consistent grouping**: All labels in a group have the same prefix and color
3. **New package structure**: Map labels to the reorganized package layout
4. **Namespace separation**: Use `A-test-*` prefix to distinguish test framework labels from future spec labels

## 📋 Label Groups

Following Rust project conventions:

| Prefix | Color | Purpose | Example |
|--------|-------|---------|---------|
| `A-*` | ![#FBCA04](https://via.placeholder.com/15/FBCA04/000000?text=+) `#FBCA04` Yellow | Area (packages, features) | `A-test-tools`, `A-test-cli-fill` |
| `C-*` | ![#C5DEF5](https://via.placeholder.com/15/C5DEF5/000000?text=+) `#C5DEF5` Light Blue | Category (bug, enhancement, etc.) | `C-bug`, `C-enhance` |
| `E-*` | ![#02E10C](https://via.placeholder.com/15/02E10C/000000?text=+) `#02E10C` Bright Green | Experience/Difficulty | `E-easy`, `E-medium`, `E-hard` |
| `F-*` | ![#D4C5F9](https://via.placeholder.com/15/D4C5F9/000000?text=+) `#D4C5F9` Purple | Ethereum Forks | `F-prague`, `F-osaka` |
| `P-*` | ![#E99695](https://via.placeholder.com/15/E99695/000000?text=+) `#E99695` Pink | Priority | `P-low`, `P-medium`, `P-high`, `P-urgent` |
| `S-*` | ![#D4C5F9](https://via.placeholder.com/15/D4C5F9/000000?text=+) `#D4C5F9` Purple | Status | `S-needs-discussion`, `S-needs-attention` |

### Key Principles

- Each issue/PR should have **at most one label from each group** (flexible for multi-area issues)
- All labels in a group share the **same color** for visual consistency
- Labels follow a **common prefix** pattern for easy filtering

## 🔧 Scripts

### 1. `label_mapping.py` - Main Migration Script

The core script that handles label creation and migration.

#### Configuration

All label mappings are defined in the `LABEL_MAPPING` dictionary:

```python
LABEL_MAPPING = {
    "old_label_name": Label("new_name", color, "description"),  # Map old → new
    "label_to_keep": "KEEP",  # Keep unchanged
    "label_to_delete": None,  # Delete without replacement
}
```

**Easy to customize**: Just edit the dictionary to change mappings!

#### Usage

**Mode 1: Create (Safe - Testing)**
```bash
# Create new labels in a test repository
uv run python scripts/label_mapping.py create --repo danceratopz/execution-specs-labels

# Dry run (show what would be created)
uv run python scripts/label_mapping.py create --repo danceratopz/execution-specs-labels --dry-run
```

**Mode 2: Migrate (Destructive - Production)**
```bash
# Full migration: create labels, update issues/PRs, delete old labels
# ⚠️  THIS MODIFIES THE REPO - USE WITH CAUTION
uv run python scripts/label_mapping.py migrate --repo ethereum/execution-spec-tests

# Dry run first!
uv run python scripts/label_mapping.py migrate --repo ethereum/execution-spec-tests --dry-run
```

#### Key Mappings

**Package Structure (A-test-*)**
```
scope:tools      → A-test-tools
scope:forks      → A-test-forks
scope:pytest     → A-test-pytest
scope:exceptions → A-test-exceptions
...
```

**CLI Commands (A-test-cli-*)**
```
scope:fill     → A-test-cli-fill
scope:consume  → A-test-cli-consume
scope:execute  → A-test-cli-execute
scope:eest     → A-test-cli-eest
scope:make     → A-test-cli-make
scope:gentest  → A-test-cli-gentest
```

**Categories (C-*)**
```
type:bug      → C-bug
type:feat     → C-enhance
type:refactor → C-refactor
type:chore    → C-chore
type:test     → C-test
type:docs     → C-doc
question      → C-question
```

**Forks (F-*)**
```
fork:prague    → F-prague
fork:osaka     → F-osaka
fork:amsterdam → F-amsterdam
```

**Status (S-*)**
```
needs-discussion → S-needs-discussion
needs-attention  → S-needs-attention
```

**Feature Consolidation**
```
feature:benchmark → A-test-benchmark
feature:zkevm     → A-test-benchmark  # Consolidated
feature:stateless → A-test-benchmark  # Consolidated
feature:eof       → A-test-eof
```

**Standard GitHub Labels Kept**
- `good first issue` - Updated to use `#02E10C` (bright green, matches `E-easy`)
- `help wanted` - Kept as-is
- `tracker` - Kept as-is
- `automated issue` - Kept as-is
- `report` - Kept as-is
- `port` - Kept as-is

### 2. `label_usage.py` - Analyze Label Usage

Check how many times each label is used across issues and PRs.

```bash
uv run python scripts/label_usage.py
```

**Output:**
- Labels with < 5 uses (candidates for deletion/consolidation)
- Full usage report sorted by count
- Helps identify unused or rarely-used labels

**Example output:**
```
Labels with < 5 uses:
  1 | feature:stateless
  1 | invalid
  2 | duplicate
  4 | t8ntools
```

### 3. `generate_mapping_html.py` - Visual HTML Report

Generate a beautiful HTML visualization of the label migration.

```bash
uv run python scripts/generate_mapping_html.py
```

**Output:** `mapping.html` with:
- Color-coded label groups
- Old → New label mappings
- Usage statistics (issues/PRs per label)
- List of new labels
- Labels kept unchanged

**Sharing the HTML:**
```bash
# Create a GitHub Gist
gh gist create mapping.html --public --desc "Label Migration Mapping"

# View rendered HTML (replace GIST_ID with your gist ID)
# https://htmlpreview.github.io/?https://gist.githubusercontent.com/USER/GIST_ID/raw/mapping.html
```

### 4. `generate_mapping_md.py` - Markdown Report

Generate a Markdown report suitable for GitHub issues and Discord.

```bash
uv run python scripts/generate_mapping_md.py
```

**Output:** `mapping.md` with:
- Markdown tables showing mappings
- Usage statistics
- Works perfectly in GitHub issues/comments
- Copy/paste friendly for Discord

## 🚀 Recommended Workflow

### Step 1: Analyze Current Labels
```bash
# Check label usage
uv run python scripts/label_usage.py
```

### Step 2: Customize Mappings

Edit `scripts/label_mapping.py`:
- Modify `LABEL_MAPPING` dictionary to change old → new mappings
- Update `NEW_LABELS` list to add labels without old mappings
- Adjust `COLORS` dictionary if needed

### Step 3: Generate Documentation

```bash
# Generate visual reports
uv run python scripts/generate_mapping_html.py
uv run python scripts/generate_mapping_md.py

# Share for review
gh gist create mapping.html --public
```

### Step 4: Test in Safe Repo

```bash
# Create labels in test repo
uv run python scripts/label_mapping.py create --repo YOUR_USERNAME/test-repo

# Review at: https://github.com/YOUR_USERNAME/test-repo/labels
```

### Step 5: Dry Run on Production

```bash
# See what would happen WITHOUT making changes
uv run python scripts/label_mapping.py migrate --repo ethereum/execution-spec-tests --dry-run
```

### Step 6: Full Migration

```bash
# ⚠️  DESTRUCTIVE - Make sure you're ready!
uv run python scripts/label_mapping.py migrate --repo ethereum/execution-spec-tests
```

## 📦 Package Structure Mapping

Based on [issue #2209](https://github.com/ethereum/execution-spec-tests/issues/2209):

```
src/ethereum_spec_tests/
├── base_types/          → A-test-base_types
├── client_clis/         → A-test-client-clis
├── config/              → A-test-config
├── ethereum_test_cli/   → A-test-ethereum_test_cli
│   ├── eest             → A-test-cli-eest
│   ├── fill             → A-test-cli-fill
│   ├── consume          → A-test-cli-consume
│   ├── execute          → A-test-cli-execute
│   ├── make             → A-test-cli-make
│   └── gentest          → A-test-cli-gentest
├── exceptions/          → A-test-exceptions
├── execution/           → A-test-execution
├── fixtures/            → A-test-fixtures
├── forks/               → A-test-forks
├── pytest/              → A-test-pytest
├── rpc/                 → A-test-rpc
├── specs/               → A-test-specs
├── tools/               → A-test-tools
├── types/               → A-test-types
└── vm/                  → A-test-vm
```

## 🎨 Design Decisions

### Why `A-test-*` prefix?

The repo will eventually contain both **specs** and **tests**. Using `A-test-*` namespaces test framework labels, leaving room for `A-spec-*` labels in the future.

### Why `F-*` for forks (not features)?

Rust uses `F-*` for features, but we use it for **Ethereum forks** (Prague, Osaka, Amsterdam). This is a legitimate domain-specific deviation since forks are a core concept in Ethereum.

### Why keep `good first issue`?

It's a widely-recognized GitHub convention that first-time contributors actively search for. We keep it AND add `E-easy` for consistency with Rust conventions. Both can be applied to the same issue.

### Why consolidate benchmark features?

Three separate features (`feature:benchmark`, `feature:zkevm`, `feature:stateless`) all related to benchmarking were consolidated into a single `A-test-benchmark` label to reduce label proliferation.

## 🔍 Common Tasks

### Add a new label mapping

Edit `scripts/label_mapping.py`:

```python
LABEL_MAPPING = {
    # ... existing mappings ...
    "old:label": Label("A-new-label", COLORS["area"], "Description here"),
}
```

### Change a label's color

```python
COLORS = {
    "area": "FBCA04",  # Change this value
    # ...
}
```

### Add a new label group

```python
# Add to COLORS
COLORS = {
    # ... existing colors ...
    "new_group": "FF0000",  # Red
}

# Add labels using the new color
LABEL_MAPPING = {
    "something": Label("N-new-group", COLORS["new_group"], "Description"),
}
```

### Skip the migration for a label

```python
LABEL_MAPPING = {
    "keep-this": "KEEP",  # Won't be changed
}
```

### Delete a label

```python
LABEL_MAPPING = {
    "delete-this": None,  # Will be deleted
}
```

## ⚠️ Important Notes

### Migration Mode (Step 2) - Not Yet Implemented

The `migrate` mode currently:
- ✅ Creates new labels
- ❌ **TODO**: Updates issues/PRs with new labels (Step 2)
- ✅ Deletes old labels

**Before running migrate mode on production:**
1. Implement Step 2 (issue/PR label updates)
2. Test thoroughly in a fork/test repo
3. Ensure you have backups/can revert

### GitHub API Rate Limits

The scripts use `gh` CLI which respects GitHub's API rate limits. For large repos with many labels/issues:
- You may hit rate limits
- Consider running during off-hours
- The `gh` CLI handles auth automatically

### Label Deletion

Labels marked as `None` in `LABEL_MAPPING` will be **deleted** during migration. Make sure:
- All issues/PRs are updated to use new labels first
- You have a backup or can recreate labels if needed

## 📚 References

- [Rust Label Triaging Guidelines](https://forge.rust-lang.org/release/issue-triaging.html)
- [execution-spec-tests Issue #2142](https://github.com/ethereum/execution-spec-tests/issues/2142) - Label migration discussion
- [execution-spec-tests Issue #2209](https://github.com/ethereum/execution-spec-tests/issues/2209) - Package restructuring
- [ethereum/execution-specs labels](https://github.com/ethereum/execution-specs/labels) - Reference implementation

## 🤝 Contributing

To modify the label migration:

1. Edit `scripts/label_mapping.py` with your changes
2. Test in a safe repo: `uv run python scripts/label_mapping.py create --repo YOUR_USERNAME/test-repo`
3. Generate reports: `uv run python scripts/generate_mapping_md.py`
4. Share for review in the relevant GitHub issue

---

*For questions or issues, see [#2142](https://github.com/ethereum/execution-spec-tests/issues/2142)*
