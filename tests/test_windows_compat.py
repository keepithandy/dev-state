from pathlib import Path
import contextlib
import io
import os
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dev_kit.cli import EXIT_SUCCESS, main as cli_main


class WindowsCompatibilityTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                exit_code = cli_main(list(args))
            except SystemExit as exc:
                exit_code = int(exc.code or 0)
        return exit_code, stdout.getvalue() + stderr.getvalue()

    def write_project(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        files = {
            "VERSION.md": "# Versión\r\n\r\nv0.1.0\r\n",
            "index.html": "<!-- café v0.1.0 -->\r\n",
            "sw.js": "// résumé v0.1.0\r\n",
            "app.js": "// naïve v0.1.0\r\n",
        }
        for name, content in files.items():
            (root / name).write_bytes(content.encode("utf-8"))

    def test_spaced_unicode_path_and_crlf_files_audit_cleanly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "Project café with spaces"
            self.write_project(root)

            exit_code, output = self.run_cli("audit", "--path", str(root))

            self.assertEqual(exit_code, EXIT_SUCCESS, output)
            self.assertIn("FAIL 0", output)
            self.assertNotIn("Traceback", output)

    def test_unicode_report_path_writes_cleanly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "Project with spaces"
            self.write_project(root)
            output_path = Path(temp_dir) / "résumé audit report.md"

            exit_code, output = self.run_cli(
                "report",
                "--path",
                str(root),
                "--output",
                str(output_path),
            )

            self.assertEqual(exit_code, EXIT_SUCCESS, output)
            self.assertTrue(output_path.exists())
            self.assertIn("# dev-kit Audit Report", output_path.read_text(encoding="utf-8"))

    @unittest.skipUnless(os.name == "nt", "drive-letter regression is Windows-specific")
    def test_drive_letter_project_path_audits_cleanly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve() / "drive-letter-project"
            self.write_project(root)
            self.assertTrue(root.drive, root)

            exit_code, output = self.run_cli("audit", "--path", str(root))

            self.assertEqual(exit_code, EXIT_SUCCESS, output)
            self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
