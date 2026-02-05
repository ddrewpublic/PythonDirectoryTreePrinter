"""
pytree_printer.py

An stdlib-only directory tree printer.

Why this exists:
- Linux has the `tree` command, but it may not be installed everywhere.
- This script produces a readable "tree diagram" using only Python's standard library.
- It can also emit **collapsible Markdown** using `<details><summary>` blocks,
  suitable for GitHub, GitLab, and most Markdown renderers.

Usage:
    python pytree_printer.py [PATH] [DEPTH]
    python pytree_printer.py [PATH] [DEPTH] --md

Examples:
    python pytree_printer.py
        # Print the tree for the current directory, depth 2.

    python pytree_printer.py LLMFilePromptWrapper 3
        # Print the tree for ./LLMFilePromptWrapper, depth 3.

    python pytree_printer.py . 3 --md > tree.md
        # Emit collapsible Markdown instead of a plain tree.

Output styles:
- Tree mode:
    - Uses box-drawing characters (├──, └──) to show hierarchy.
    - Appends "/" to directory names.
- Markdown mode:
    - Uses nested <details><summary> blocks.
    - Preserves tree-style indentation visually.

Defaults:
- Skips common noise directories like .git and __pycache__.
- Directories are listed before files, then alphabetically.
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
__version__ = "0.3.0"

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
    """Return the installed package version if available.

    Attempts to read the version from installed package metadata.
    Falls back to the local ``__version__`` constant if unavailable.

    Returns:
        str: Semantic version string (e.g. "0.3.0").
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
    """Normalize a path to a POSIX-style relative string.

    Args:
        path: Path to normalize.

    Returns:
        str: Relative path using forward slashes, without leading "./".
    """
    return path.as_posix().lstrip("./")


def _should_ignore(
        *,
        root: Path,
        path: Path,
        ignore_names: set[str],
        ignore_globs: Iterable[str],
        ignore_paths: set[Path],
) -> bool:
    """Determine whether a path should be excluded from output.

    Matching rules:
    - Exact name match against ``ignore_names``
    - Relative path match against ``ignore_paths`` (relative to ``root``)
    - Glob match against either:
        - the basename (e.g. "*.pyc")
        - the relative path (e.g. "**/.venv/**")

    Args:
        root: Root directory of the tree walk.
        path: Candidate path to test.
        ignore_names: Exact filenames or directory names to skip.
        ignore_globs: Glob patterns to skip.
        ignore_paths: Explicit relative paths to skip.

    Returns:
        bool: True if the path should be ignored.
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


def print_tree_md(
        root: Path,
        max_depth: int = 2,
        *,
        ignore_names: set[str] | None = None,
        ignore_globs: Iterable[str] = (),
        ignore_paths: Iterable[Path] = (),
        include_files: bool = True,
) -> None:
    """Print a directory tree as collapsible Markdown.

    Output uses nested ``<details><summary>`` blocks, suitable for
    GitHub, GitLab, and most HTML-capable Markdown renderers.

    Args:
        root: Directory to print.
        max_depth: Maximum traversal depth.
        ignore_names: Exact directory/file names to skip.
        ignore_globs: Glob patterns to skip.
        ignore_paths: Paths (relative to root) to skip.
        include_files: If False, print directories only.
    """
    root = root.resolve()

    ignore_names = set(DEFAULT_IGNORE_NAMES if ignore_names is None else ignore_names)
    ignore_globs = tuple(DEFAULT_IGNORE_GLOBS) + tuple(ignore_globs)
    ignore_paths_set = {Path(p) for p in ignore_paths}

    print(f"<details><summary>{root.name}/</summary>")

    def walk(dir_path: Path, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return

        entries: list[Path] = []
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

            # convert tree prefix to nbsp
            md_prefix = (
                prefix
                .replace("│", "&nbsp;")
                .replace(" ", "&nbsp;")
            )

            print(
                f"{'    ' * (depth + 1)}"
                f"<details><summary>{md_prefix}{connector}{name}</summary>"
            )

            if p.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                walk(p, child_prefix, depth + 1)

            print(f"{'    ' * (depth + 1)}</details>")

    walk(root, prefix="", depth=0)
    print("</details>")


def print_tree(
        root: Path,
        max_depth: int = 2,
        *,
        ignore_names: set[str] | None = None,
        ignore_globs: Iterable[str] = (),
        ignore_paths: Iterable[Path] = (),
        include_files: bool = True,
) -> None:
    """Print a directory tree using box-drawing characters.

    Args:
        root: Directory to print.
        max_depth: Maximum traversal depth.
        ignore_names: Exact directory/file names to skip.
        ignore_globs: Glob patterns to skip.
        ignore_paths: Paths (relative to root) to skip.
        include_files: If False, print directories only.

    Notes:
        - Does not follow symlinks.
        - Directories are listed before files, then alphabetically.
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
    """CLI entry point.

    Parses command-line arguments and dispatches to the appropriate
    output mode (tree or Markdown).

    Args:
        argv: Optional argument list (defaults to ``sys.argv``).

    Returns:
        int: Process exit code.
    """
    argv = sys.argv[1:] if argv is None else argv

    fmt = "tree"
    if "--md" in argv:
        fmt = "md"
        argv.remove("--md")

    target = Path(argv[0]) if len(argv) > 0 else Path(".")
    depth = int(argv[1]) if len(argv) > 1 else 2

    if fmt == "md":
        print_tree_md(target, max_depth=depth)
    else:
        print_tree(target, max_depth=depth)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
