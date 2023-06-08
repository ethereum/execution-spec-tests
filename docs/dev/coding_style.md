# Coding Style

## Formatting and Line Length

The Python code in execution-spec-tests is black formatted with a maximum line length of 100. Using VS Code with `editor.formatOnSave` is a big help to ensure files conform to the repo's coding style, see [VS Code Setup](../getting_started/setup_vs_code.md) to configure this and other useful settings.

### Ignoring Bulk Change Commits

The max line length was changed from 80 to 100 in Q2 2023. To ignore this bulk change commit in git blame output, use the `.git-blame-ignore-revs` file, for example:

```console
git blame --ignore-revs-file .git-blame-ignore-revs docs/gen_filler_pages.py
```

To use the revs file persistently with `git blame`, run

```console
git config blame.ignoreRevsFile .git-blame-ignore-revs
```
