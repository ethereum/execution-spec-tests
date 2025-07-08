# HUMANS.md - Working with Claude and LLMs in Ethereum Execution Spec Tests

This guide helps human developers understand the dependencies and get the most out of Claude and other LLMs when working with this codebase.

## 🤖 Why This Repository Has LLM Support

Humans are faster when they use LLMs correctly.

## 📋 Required Dependencies for LLM-Assisted Development

### Requirements

#### LLM Context File

- **CLAUDE.md** - Primary LLM guidance (keep up-to-date). Use `#memorize` in Claude to update with new info.

### Recommended Available Tooling (for use with Claude)

1. **GitHub CLI**: `gh` for PR and issue management.
2. **ripgrep**: `rg` for fast code searching.
3. **jq**: For JSON analysis and EVM trace debugging.
4. **markdownlint-cli**: To verify markdown files (CI enforced).
5. **VS Code**: With recommended extensions (see [setup guide](docs/getting_started/setup_vs_code.md)). Run `claude` in VS Code for the best results.

## 🎯 Getting the Best Results from Claude

### 1. Provide Relevant Context

**Always mention:**

- What you're trying to accomplish.
- Which part of the codebase you're working on (`tests/`, `src/`, `docs/`).
- Any error messages or specific issues you're encountering.

**Example - Good Context**:
> "I'm writing a new test for EIP-7702 in `tests/prague/eip7702_set_code_tx/`. The test should verify that delegation target validation works correctly. The test fails to fill when running `uv run fill --fork=Prague path/to/test.py`"

**Example - Poor Context**:
> "My test isn't working"

### 2. Reference Key Documentation

When asking Claude for help, mention which documentation you've already checked:

- "I've read the test patterns in CLAUDE.md but...".
- "According to the debugging section in CLAUDE.md...".
- "The CONTRIBUTING.md mentions X, but I need help with Y...".

### 3. Share Specific Commands and Output

Claude works best with concrete information:

```bash
# Share the exact command you ran
uv run fill --fork=Prague tests/cancun/eip4844_blobs/test_blob_txs.py --clean -v

# Include relevant error output
ERROR: Failed to compile Yul source: ...
```

### 4. Ask for Complete Solutions

Request end-to-end guidance rather than partial answers:

- "Show me the complete test function with proper imports.".
- "What's the full workflow from creating the test to verifying it works?".
- "Include the commands I need to run to validate this change.".

## 🚀 Optimizing LLM Workflows

### Quick Start Template

When starting a new (and complicated) task, provide Claude with something similar to template.

```console
I'm working on [describe task] in the Ethereum execution-spec-tests repository.

**Context**:
- Working directory: [tests/shanghai/, src/ethereum_test_tools/, etc.]
- Trying to: [specific goal]
- Current status: [what you've tried, any errors]

**References**:
- Checked CLAUDE.md section: [which sections you've read]
- Related documentation: [any other docs you've reviewed]

**Specific question**: [exactly what you need help with]
```

### Debugging Template

For troubleshooting issues:

```console
I'm encountering [specific error] when [doing what].

**Command run**:
```bash
[exact command that failed]
```console

**Error output**:

```
[full error message]
```console

**What I've tried**:

- [list previous attempts].

**Environment details**:

```bash
uv run eest info
```console

**Request**: Please help me understand what's wrong and provide the fix.

```

### Code Review Template

When asking Claude to review code:

```console

Please review this [test/function/module] for:

- Compliance with project standards (CLAUDE.md, code_standards.md).
- Correct usage of the `pre` fixture.
- Proper error handling and type annotations.
- Performance considerations.

**Code**:

```python
[your code here]
```console

**Specific concerns**: [any particular areas you're unsure about]

## 🧠 Understanding LLM Limitations

### What Claude Excels At

- ✅ **Code patterns and structure**.
- ✅ **Following established conventions**.
- ✅ **Debugging common issues**.
- ✅ **Explaining complex concepts**.
- ✅ **Generating boilerplate code**.
- ✅ **Reviewing code for standards compliance**.

### What to Verify Independently

- ⚠️ **Latest dependency versions** (always check official docs).
- ⚠️ **New EIP specifications** (verify against ethereum/EIPs).
- ⚠️ **Breaking changes** in recent updates.
- ⚠️ **Environment-specific issues** (OS, architecture).
- ⚠️ **Security implications** of suggestions.

### For Effective LLM Collaboration

- Provide clear, specific prompts.
- Break complex tasks into smaller pieces.
- Always validate LLM output against standards.
- Use the codebase's existing patterns as examples.

Remember: **LLMs are powerful tools that work best when given good context and clear objectives.** The better you understand this codebase, the better you can guide Claude to help you effectively.
