"""salvage test suite."""
import contextlib
import io
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# Tool under test (imported so the test also exercises the scan() helper).
import tools.salvage.main as salvage


def run_salvage(binary):
    proc = subprocess.run(
        [sys.executable, "-m", "tools.salvage", str(binary)],
        capture_output=True, text=True, check=True,
    )
    return proc.stdout


def make_fixture(filepath, strings):
    data = b""
    for s in strings:
        data += s.encode("ascii") + b"\x00"
    filepath.write_bytes(data)


class SalvageScanTest(unittest.TestCase):
    def test_top_candidate_strings_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "dump.bin"
            make_fixture(blob, ["kSecondBank", "kFirstBank", "kSlotMask", "kSlotMask"])
            out = run_salvage(blob)
        self.assertIn("kSlotMask", out)
        self.assertIn("kFirstBank", out)
        self.assertIn("kSecondBank", out)

    def test_small_files_produce_empty_output(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "tiny.bin"
            blob.write_bytes(b"\x00" * 8)
            out = run_salvage(blob)
        self.assertIn("total candidate strings", out)
        self.assertIn("0", out)


if __name__ == "__main__":
    unittest.main()
