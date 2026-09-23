"""Path-boundary helpers for dev-kit CLI safety."""

from __future__ import annotations

import os
from pathlib import Path

GENERATED_REPORT_HEADERS = (
    "# dev-kit Audit Report",
    "# dev-kit Portfolio Audit Report",
)


def path_uses_link_or_junction(path_value: str | Path) -> bool:
    """Return True when resolving the path changes its lexical absolute location.

    On POSIX this catches symlinked path components. On Windows, ``realpath`` also
    resolves junction/reparse-point components supported by the Python runtime.
    Missing leaf paths are allowed; existing linked parent components are still
    detected.
    """

    expanded = os.fspath(Path(path_value).expanduser())
    lexical = os.path.normcase(os.path.abspath(expanded))
    resolved = os.path.normcase(os.path.realpath(expanded))
    return lexical != resolved


def path_is_within(path: Path, root: Path) -> bool:
    """Return True when *path* resolves to *root* or one of its descendants."""

    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def is_generated_report(path: Path) -> bool:
    """Recognize report files previously written by dev-kit."""

    if not path.exists() or not path.is_file() or path.is_symlink():
        return False

    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            first_line = handle.readline().strip()
    except OSError:
        return False

    return first_line in GENERATED_REPORT_HEADERS
