"""savemap test suite."""

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_savemap(old_path, new_path, capture=True):
    proc = subprocess.run(
        [sys.executable, "-m", "tools.savemap", str(old_path), str(new_path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def make_pair(old_content, new_content):
    with tempfile.TemporaryDirectory() as d:
        old = pathlib.Path(d) / "old.bin"
        new = pathlib.Path(d) / "new.bin"
        old.write_bytes(old_content)
        new.write_bytes(new_content)
        return old, new


class SavemapDiffTest(unittest.TestCase):
    def test_identical_files_are_reported_as_identical(self):
        old = b"\x41" * 0x20
        new = b"\x41" * 0x20
        with tempfile.TemporaryDirectory() as d:
            old_p = pathlib.Path(d) / "old.bin"
            new_p = pathlib.Path(d) / "new.bin"
            old_p.write_bytes(old)
            new_p.write_bytes(new)
            out = run_savemap(old_p, new_p)
        self.assertIn("identical", out)
        self.assertNotIn("changed region", out)

    def test_changed_region_reported_as_range(self):
        # 256 bytes. Offset 0x10..0x15 differ.
        old = bytearray(0x200)
        new = bytearray(0x200)
        old[0x10:0x16] = b"ABCDEF"
        new[0x10:0x16] = b"XYZ123"
        with tempfile.TemporaryDirectory() as d:
            old_p = pathlib.Path(d) / "old.bin"
            new_p = pathlib.Path(d) / "new.bin"
            old_p.write_bytes(bytes(old))
            new_p.write_bytes(bytes(new))
            out = run_savemap(old_p, new_p)
        self.assertIn("changed region", out)
        self.assertIn("00000010-00000015", out)

    def test_full_file_hashes_are_printed(self):
        old = b"AAAA"
        new = b"AAAB"
        with tempfile.TemporaryDirectory() as d:
            p_old = pathlib.Path(d) / "old.bin"
            p_new = pathlib.Path(d) / "new.bin"
            p_old.write_bytes(old)
            p_new.write_bytes(new)
            out = run_savemap(p_old, p_new)
        self.assertIn("SHA256", out)
        self.assertIn("41414141", out)
        self.assertIn("41414142", out)


if __name__ == "__main__":
    unittest.main()
