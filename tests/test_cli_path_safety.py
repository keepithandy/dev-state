from pathlib import Path
import contextlib
import io
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dev_kit.cli import EXIT_SUCCESS, EXIT_USAGE_ERROR, main as cli_main


def write_clean_project(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "VERSION.md").write_text("# Version\n\nv0.1.0\n", encoding="utf-8")
    (root / "index.html").write_text("<!-- v0.1.0 -->\n", encoding="utf-8")
    (root / "sw.js").write_text("// v0.1.0\n", encoding="utf-8")
    (root / "app.js").write_text("// v0.1.0\n", encoding="utf-8")


class CliPathSafetyTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exit_code = cli_main(list(args))
            except SystemExit as exc:
                exit_code = int(exc.code or 0)
        return exit_code, stdout.getvalue() + stderr.getvalue()

    def test_report_refuses_to_overwrite_existing_project_source_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_clean_project(root)
            original = (root / "VERSION.md").read_text(encoding="utf-8")

            exit_code, output = self.run_cli(
                "report",
                "--path",
                str(root),
                "--output",
                str(root / "VERSION.md"),
            )

            self.assertEqual(exit_code, EXIT_USAGE_ERROR)
            self.assertIn("Refusing to overwrite an existing project file", output)
            self.assertEqual((root / "VERSION.md").read_text(encoding="utf-8"), original)
            self.assertNotIn("Traceback", output)

    def test_report_can_replace_a_previous_dev_kit_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "project"
            write_clean_project(root)
            report = root / "devkit-report.md"
            report.write_text("# dev-kit Audit Report\n\nold report\n", encoding="utf-8")

            exit_code, output = self.run_cli(
                "report",
                "--path",
                str(root),
                "--output",
                str(report),
            )

            self.assertEqual(exit_code, EXIT_SUCCESS, output)
            self.assertIn("Wrote report:", output)
            self.assertTrue(report.read_text(encoding="utf-8").startswith("# dev-kit Audit Report"))

    def test_symlinked_project_root_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks are not supported on this platform")

        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            target = parent / "actual-project"
            link = parent / "linked-project"
            write_clean_project(target)
            try:
                os.symlink(target, link, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"cannot create directory symlink: {exc}")

            exit_code, output = self.run_cli("audit", "--path", str(link))

            self.assertEqual(exit_code, EXIT_USAGE_ERROR)
            self.assertIn("symlink or junction", output)
            self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
