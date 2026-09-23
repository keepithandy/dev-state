# dev-kit Quality Gates

This document describes the repository checks that protect dev-kit itself and the path-safety behavior expected by local users.

## Local parity

Run the same core checks used by CI from the repository root:

```powershell
python -m pip install -e .
python -m unittest discover -s tests
python -m dev_kit --help
python -m dev_kit audit --path tests\fixtures\clean_project
```

On bash/macOS/Linux, use `/` separators for the fixture path.

## Python CI matrix

GitHub Actions runs the unit suite, CLI help, and a clean fixture audit on:

- Ubuntu with Python 3.10
- Ubuntu with Python 3.12
- Windows with Python 3.10
- Windows with Python 3.12

This keeps the minimum supported Python version covered while also exercising a newer runtime and PowerShell-first Windows path behavior.

## Package smoke

The package smoke workflow:

1. Builds both a wheel and source distribution.
2. Verifies expected package files and metadata are present.
3. Creates a clean virtual environment.
4. Installs the built wheel rather than the source checkout.
5. Verifies installed package version metadata.
6. Runs `dev-kit --help`.
7. Runs a clean fixture audit.

The workflow does not publish to PyPI, create tags, or create releases.

## Path and encoding expectations

Supported project paths include:

- normal absolute and relative paths
- Windows drive-letter paths
- directory and file names containing spaces
- Unicode directory and file names
- UTF-8 text
- CRLF or LF line endings

Paths that cross symlinks or Windows junction/reparse-point aliases are rejected by the CLI. Use the resolved physical path directly instead. This makes the audit boundary explicit and prevents an apparently local path from silently resolving elsewhere.

Missing project roots, file paths supplied where directories are expected, and invalid output parents return stable usage errors without Python tracebacks.

## Report overwrite protection

`report` and `portfolio --output` may create a new report at the exact requested path. When the requested output already exists inside the protected audited root, dev-kit only overwrites it when the file is recognizable as a previously generated dev-kit audit report.

Existing source files such as `README.md`, `VERSION.md`, application code, or unrelated Markdown files are refused as report overwrite targets. Existing output files outside the protected audited root remain an explicit user choice.

## Repository integrity smoke

The repository-integrity workflow remains a separate lightweight gate for repository-level corruption indicators such as conflict markers, invalid JSON, NUL bytes in text files, and oversized files.
