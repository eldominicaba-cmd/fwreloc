"""Tests for the binmeta tool (binary fingerprint)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_binmeta(binary, extra=()):
    cmd = [sys.executable, "-m", "tools.binmeta", str(binary)] + list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def write_fixture(path, data):
    path.write_bytes(data)


class BinmetaTest(unittest.TestCase):
    def test_fingerprint_on_real_binary(self):
        with tempfile.TemporaryDirectory() as d:
            ls = pathlib.Path("/bin/ls")
            blob = pathlib.Path(d) / "bin.ls"
            blob.write_bytes(ls.read_bytes())
            out = run_binmeta(blob)
        self.assertIn("sha256", out)
        self.assertIn("856d15c5351af43f30fcd151291f6e38b8301c931f9089903cc3be434a95faef", out)
        self.assertIn("size", out)
        self.assertIn("ELF", out)
        self.assertIn("machine=0x3e", out)

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "bin.ls"
            blob.write_bytes(pathlib.Path("/bin/ls").read_bytes())
            out = run_binmeta(blob, ["-f", "json"])
        self.assertIn("sha256", out)
        self.assertIn("section_count", out)
        self.assertIn("29", out)

    def test_non_elf_binary(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "raw.bin"
            blob.write_bytes(b"\xb8\x01\x00\x00" + b"\x00" * 10)
            out = run_binmeta(blob)
        self.assertIn("b8010000", out)
        self.assertIn("unknown", out)

    def test_missing_file_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run(
                [sys.executable, "-m", "tools.binmeta", "nope.bin"],
                capture_output=True, text=True,
            )
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
