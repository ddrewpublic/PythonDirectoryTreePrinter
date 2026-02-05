# Python Directory Tree Printer

A tiny, stdlib-first directory tree printer that outputs a readable tree diagram of a folder. Like `tree(1)`, but in
Python - useful when you're on a machine where `tree` isn't installed, or you want something you can install into a
project without too much fuss.

## Features

- Prints a directory tree using box-drawing characters (`├──`, `└──`)
- Appends `/` to directory names
- Limits traversal depth
- Skips common junk directories by default:
    - `.git`
    - `__pycache__`
    - `.mypy_cache`
    - `.pytest_cache`
- **Optional Markdown output** using collapsible `<details><summary>` blocks
- Includes a simple version lookup helper (`get_package_version()`), with safe fallbacks

## Requirements

- Python 3.8+ (recommended)
- Python 3.7 can work **if** you install the backport:
    - `importlib-metadata`

> If you're on Python 3.8+, `importlib.metadata` is in the standard library.

## File Overview

This project's main entry point is:

- `src/pytree_printer.py`

Key functions:

- `print_tree(root: Path, max_depth: int = 2) -> None`
- `print_tree_md(root: Path, max_depth: int = 2) -> None`
- `get_package_version() -> str`

## Usage

### Run as a script

```bash
python pytree_printer.py
python pytree_printer.py /path/to/somewhere
python pytree_printer.py /path/to/somewhere 3
```

### Markdown output

```bash
python pytree_printer.py /path/to/somewhere 3 --md > tree.md
```

### Using it from your own code

```python
from pathlib import Path
from pytree_printer import print_tree, print_tree_md

print_tree(Path("LLMFilePromptWrapper"), max_depth=2)
print_tree_md(Path("LLMFilePromptWrapper"), max_depth=2)
```

## Installation

```bash
echo "utilities-custom-logger @ git+ssh://git@github.com/ddrewpublic/pythondirectorytreeprinter.git@v0.1.0" | tee -a requirements.txt
pip install -r requirements.txt
```

## Upgrade

```bash
pip install --upgrade --force-reinstall --no-cache-dir "git+ssh://git@github.com/ddrewpublic/pythondirectorytreeprinter.git@main"
```

## Versioning

`get_package_version()` tries to read installed distribution metadata:

- Distribution name: python_directory_tree_printer (matches pyproject.toml)
- Fallback: module constant `__version__ = "0.1.0"`

If the package isn't installed (e.g., you're just running the file directly), it won't crash - it'll return the fallback
version.

## Notes

- Does not follow symlinks
- Prints to stdout
