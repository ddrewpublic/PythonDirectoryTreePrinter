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

import fnmatch
import sys
from pathlib import Path
from typing import Iterable

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

DEFAULT_IGNORE_NAMES: set[str] = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".idea",
    ".venv",
    ".gitignore",
}

DEFAULT_IGNORE_GLOBS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    ".gitignore",
)


def _get_package_version() -> str:
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


def _norm_rel(path: Path) -> str:
    """Return a normalized, POSIX-style relative path string."""
    return path.as_posix().lstrip("./")


def _should_ignore(
        *,
        root: Path,
        path: Path,
        ignore_names: set[str],
        ignore_globs: Iterable[str],
        ignore_paths: set[Path],
) -> bool:
    """
    Decide whether `path` should be ignored.

    Matching rules:
    - Exact name match against `ignore_names`
    - Relative path match against `ignore_paths` (relative to `root`)
    - Glob match against:
        - basename (e.g. "*.pyc")
        - relative path (e.g. "build/**", "**/.venv/**")
    """
    name = path.name
    if name in ignore_names:
        return True

    try:
        rel = path.relative_to(root)
    except ValueError:
        # If it's not under root for some reason, don't ignore by path rules.
        rel = path

    if rel in ignore_paths:
        return True

    rel_s = _norm_rel(rel)
    for pat in ignore_globs:
        # Match either the filename or the relative path
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel_s, pat):
            return True

    return False


def print_tree(
        root: Path,
        max_depth: int = 2,
        *,
        ignore_names: set[str] | None = None,
        ignore_globs: Iterable[str] = (),
        ignore_paths: Iterable[Path] = (),
        include_files: bool = True,
) -> None:
    """
    Print a directory tree for `root` up to `max_depth` levels deep.

    Args:
        root: Directory to print.
        max_depth: Maximum depth to traverse.
        ignore_names: Exact directory/file names to skip (e.g. {".git", "__pycache__"}).
        ignore_globs: Glob patterns to skip (e.g. ("*.pyc", "dist/**", "**/.venv/**")).
        ignore_paths: Paths (relative to root) to skip (e.g. [Path("node_modules")]).
        include_files: If False, prints directories only.

    Notes:
        - Does not follow symlinks.
        - Directories are listed before files, then alphabetical.
    """
    root = root.resolve()

    ignore_names = set(DEFAULT_IGNORE_NAMES if ignore_names is None else ignore_names)
    ignore_globs = tuple(DEFAULT_IGNORE_GLOBS) + tuple(ignore_globs)
    ignore_paths_set = {Path(p) for p in ignore_paths}

    print(f"{root.name}/")

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return

        entries = []
        for p in dir_path.iterdir():
            if _should_ignore(
                    root=root,
                    path=p,
                    ignore_names=ignore_names,
                    ignore_globs=ignore_globs,
                    ignore_paths=ignore_paths_set,
            ):
                continue
            if not include_files and p.is_file():
                continue
            entries.append(p)

        entries.sort(key=lambda p: (p.is_file(), p.name.lower()))

        for i, p in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            name = p.name + ("/" if p.is_dir() else "")
            print(prefix + connector + name)

            if p.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                walk(p, child_prefix, depth + 1)

    walk(root, prefix="", depth=0)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    target = Path(argv[0]) if len(argv) > 0 else Path(".")
    depth = int(argv[1]) if len(argv) > 1 else 2
    print_tree(target, max_depth=depth)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
