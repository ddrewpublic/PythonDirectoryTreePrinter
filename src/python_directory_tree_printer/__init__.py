# src/pytree_printer/__init__.py
# comment: re-export main public API from the custom_logger module
from .pytree_printer import print_tree, get_package_version

# comment: public symbols for `from utilities_custom_logger import *`
__all__ = [
    "print_tree",
    "__version__"
]

# comment: package-level version, sourced from pyproject.toml via get_logger_version()
__version__ = get_package_version()
