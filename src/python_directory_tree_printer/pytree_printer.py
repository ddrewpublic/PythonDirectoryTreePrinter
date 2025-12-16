"""
pytree_printer.py

A tiny, stdlib-only directory tree printer.

Why this exists:
- Linux has the `tree` command, but it may not be installed everywhere.
- This script produces a readable "tree diagram" using only Python's standard library.

Usage:
    python pytree_printer.py [PATH] [DEPTH]

Examples:
    python pytree_printer.py
        # Print the tree for the current directory, depth 2.

    python pytree_printer.py LLMFilePromptWrapper 3
        # Print the tree for ./LLMFilePromptWrapper, depth 3.

Output style:
- Uses box-drawing characters (├──, └──) to show hierarchy.
- Appends "/" to directory names.
- Skips common noise directories like .git and __pycache__ by default.
"""

from __future__ import annotations

import sys
from pathlib import Path

# --- version metadata -------------------------------------------------------
# comment: compat import for Python 3.7–3.10+
try:
    # Python 3.8+
    from importlib.metadata import PackageNotFoundError, version as _pkg_version  # noqa
except ImportError:  # Python < 3.8
    from importlib_metadata import (  # type: ignore[import]
        PackageNotFoundError,
        version as _pkg_version,
    )

_PACKAGE_NAME = "python_directory_tree_printer"  # matches pyproject.toml
# Optional fallback module-defined version if metadata not available
__version__ = "0.1.0"


def get_package_version() -> str:
    """Return the version string for this logging utility.

    Resolution order:
        1. Installed package metadata for `utilities_custom_logger`
           (from pyproject.toml).
        2. Local ``__version__`` constant as a fallback.

    Returns:
        str: Semantic version string, e.g. "0.3.0".
    """
    try:
        return _pkg_version(_PACKAGE_NAME)
    except PackageNotFoundError:
        # Not installed as a package – fall back to local constant.
        return __version__
    except Exception:  # noqa
        # Defensive: never let version lookup break logging.
        return __version__


def print_tree(root: Path, max_depth: int = 2) -> None:
    """
    Print a directory tree for `root` up to `max_depth` levels deep.

    Args:
        root: Directory to print.
        max_depth: Maximum depth to traverse.
            Depth is counted from `root`:
              - depth 0: root itself (always printed)
              - depth 1: root's direct children
              - depth 2: grandchildren
              - etc.

    Notes:
        - This function is intentionally conservative and avoids following symlinks.
        - It filters out a couple of common "junk" directories.
    """
    root = root.resolve()

    # Print the root folder name as the header line.
    print(f"{root.name}/")

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        """
        Recursive helper that prints entries in `dir_path`.

        Args:
            dir_path: The directory currently being printed.
            prefix: The indentation + vertical bars used to align children.
            depth: Current depth relative to the root.
        """
        # Stop recursion once we hit the configured depth.
        if depth >= max_depth:
            return

        # Gather directory entries, skipping common clutter.
        # Sorting rule:
        #   - directories first, then files
        #   - alphabetical within each group
        entries = sorted(
            [
                p
                for p in dir_path.iterdir()
                if p.name not in {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
            ],
            key=lambda p: (p.is_file(), p.name.lower()),
        )

        for i, p in enumerate(entries):
            # Determine whether this is the last entry so we can draw the right connector.
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            # Add "/" suffix for directories to make the output easier to scan.
            name = p.name + ("/" if p.is_dir() else "")
            print(prefix + connector + name)

            # Recurse into subdirectories, extending the prefix so the tree lines align.
            if p.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                walk(p, child_prefix, depth + 1)

    # Start recursion from the root with no prefix at depth 0.
    walk(root, prefix="", depth=0)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    target = Path(argv[0]) if len(argv) > 0 else Path(".")
    depth = int(argv[1]) if len(argv) > 1 else 2
    print_tree(target, max_depth=depth)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
