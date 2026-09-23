"""Path-boundary helpers for dev-kit CLI safety."""

from __future__ import annotations

import os
from pathlib import Path
import stat

GENERATED_REPORT_HEADERS = (
    "# dev-kit Audit Report",
    "# dev-kit Portfolio Audit Report",
)


def _is_reparse_point(path: Path) -> bool:
    """Return True for Windows reparse points without requiring Python 3.12."""

    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if not reparse_flag:
        return False

    try:
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & reparse_flag)


def path_uses_link_or_junction(path_value: str | Path) -> bool:
    """Return True when an existing path component is a symlink or junction.

    The check walks lexical path components instead of comparing ``abspath`` with
    ``realpath``. That avoids false positives caused by Windows path spelling or
    short-name normalization while still detecting POSIX symlinks and Windows
    reparse-point/junction components. Missing leaf paths are allowed.
    """

    current = Path(os.path.abspath(os.fspath(Path(path_value).expanduser())))

    while True:
        if current.exists():
            try:
                if current.is_symlink() or _is_reparse_point(current):
                    return True
            except OSError:
                pass

        parent = current.parent
        if parent == current:
            break
        current = parent

    return False


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
