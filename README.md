# Python Directory Tree Printer

A tiny, stdlib-first directory tree printer that outputs a readable "tree diagram" of a folder. Like `tree(1)`, but in
Python - useful when you're on a machine where `tree` isn't installed, or you want something you can vendor into a
project without drama.

## Features

- Prints a directory tree using box-drawing characters (`├──`, `└──`)
- Appends `/` to directory names
- Limits traversal depth
- Skips common junk directories by default:
    - `.git`
    - `__pycache__`
    - `.mypy_cache`
    - `.pytest_cache`
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
  Prints the directory tree.
- `get_package_version() -> str`  
  Returns the installed package version if available, otherwise falls back to `__version__`.

## Usage

### Run as a script

From the directory containing `pytree_printer.py`:

```bash
python pytree_printer.py
```

Print a specific directory:

```bash
python pytree_printer.py /path/to/somewhere
```

Limit depth (example: 3 levels):

```bash
python pytree_printer.py /path/to/somewhere 3
```

### Example output

Given:

```bash
LLMFilePromptWrapper/
  utilities/
  _testing/
```

You'll get something like:

```bash
LLMFilePromptWrapper/
├── _testing/
└── utilities/
```

(Exact ordering depends on names; directories are listed before files.)

### Using it from your own code

```bash
from pathlib import Path
from pytree_printer import print_tree

print_tree(
    Path("."),
    max_depth=4,
    ignore_globs=("dist/**", "build/**", "**/.venv/**", "*.log"),
    ignore_paths=(Path("node_modules"), Path("src/generated")),
)
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

## Notes / Gotchas

- This intentionally does not follow symlinks.
- It prints to `stdout` (no return value). If you want a string output, you can redirect `stdout` or refactor to build a
  list of lines.
- The ignore list is hardcoded in `print_tree()`; tweak it if you want to include `.git` or caches.
