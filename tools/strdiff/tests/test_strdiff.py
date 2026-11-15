"""Tests for the strdiff tool (string-level diff between two binaries)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_strdiff(old, new):
    proc = subprocess.run(
        [sys.executable, "-m", "tools.strdiff", str(old), str(new)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def write_dump(path, strings):
    data = b""
    for s in strings:
        data += s.encode("ascii") + b"\x00"
    path.write_bytes(data)


class StrDiffTest(unittest.TestCase):
    def test_diff_reports_added_removed_shared(self):
        with tempfile.TemporaryDirectory() as d:
            old = pathlib.Path(d) / "old.bin"
            new = pathlib.Path(d) / "new.bin"
            old_strings = ["kSlotMask", "kProtoV2", "kSecondBank", "uBoot", "FW_VERSION"]
            new_strings = ["kSlotMask2", "kProtoV2", "kSecondBank",
                           "uBoot", "FW_VERSION", "kPatchVer"]
            write_dump(old, old_strings)
            write_dump(new, new_strings)
            out = run_strdiff(old, new)
        self.assertIn("strdiff: ", out)
        self.assertIn("shared     : 4", out)
        self.assertIn("added      : 2", out)
        self.assertIn("removed    : 1", out)
        self.assertIn("kSlotMask2", out)
        self.assertIn("kPatchVer", out)
        self.assertIn("kSlotMask", out)

    def test_identical_files_reported_with_zero_diffs(self):
        data = b"\x00" * 64
        with tempfile.TemporaryDirectory() as d:
            old = pathlib.Path(d) / "old.bin"
            new = pathlib.Path(d) / "new.bin"
            old.write_bytes(data)
            new.write_bytes(data)
            out = run_strdiff(old, new)
        self.assertIn("shared     : 0", out)
        self.assertIn("added      : 0", out)
        self.assertIn("removed    : 0", out)

    def test_missing_file_fails_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            old = pathlib.Path(d) / "old.bin"
            out = subprocess.run(
                [sys.executable, "-m", "tools.strdiff", str(old), "nope.bin"],
                capture_output=True, text=True,
            )
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
