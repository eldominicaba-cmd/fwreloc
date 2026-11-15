"""Tests for the sigscan tool (signature / string scan)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_sigscan(binary, *patterns, common=False):
    cmd = [sys.executable, "-m", "tools.sigscan", str(binary)]
    if common:
        cmd.append("--common")
    cmd += list(patterns)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def write_dump(path, payload):
    path.write_bytes(payload)


class SigScanTest(unittest.TestCase):
    def test_find_hex_and_ascii_patterns(self):
        # bytes: MZ(0) then 43 76 55 at 2, then "kProtoV2"
        payload = b"MZ" + b"\x43\x76\x55" + b"kProtoV2" + b"\x00"
        blob = pathlib.Path("blob.bin")
        write_dump(blob, payload)
        try:
            out = run_sigscan(blob, "43 76 55", "kProtoV2")
        finally:
            blob.unlink()
        self.assertIn("43 76 55", out)
        self.assertIn("kProtoV2", out)
        self.assertIn("1", out)          # one hex match
        self.assertIn("1", out)          # one string match

    def test_common_magic_signatures(self):
        blob = pathlib.Path("blob.bin")
        write_dump(blob, b"MZ" + bytes(range(64)))  # MZ at offset 0
        try:
            out = run_sigscan(blob, common=True)
        finally:
            blob.unlink()
        self.assertIn("4d5a", out)
        self.assertIn("1 @ [0]", out)

    def test_missing_file_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run(
                [sys.executable, "-m", "tools.sigscan", "nope.bin", "43"],
                capture_output=True, text=True,
            )
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
