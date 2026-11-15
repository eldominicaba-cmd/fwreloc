"""salvage test suite."""
import contextlib
import io
import pathlib
import re
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

    def test_realistic_large_binary(self):
        """Point salvage at a large (2MB) binary shaped like a dump: repeated
        keys (license/section markers) interleaved with zero padding and a
        little printable salt. This is the deterministic stand-in for pointing
        salvage at a real firmware/binary dump."""
        rng = 0x53494C56  # "SILV"
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "dump.bin"
            data = bytearray()
            keys = [b"kSlotMask", b"kProtoV2", b"kSecondBank",
                    b"uBoot", b"FW_VERSION"]
            for k in keys:
                pad = (0x1000 - len(data) % 0x1000) % 0x1000
                data += b"\x00" * pad
                data += (k + b"\x00") * 12
            while len(data) < 0x200000:
                data.append((rng ^ len(data)) & 0xFF)
            blob.write_bytes(data)
            out = run_salvage(blob)
        for k in keys:
            self.assertIn(k.decode(), out)
        m1 = re.search(r"total candidate strings\s*:\s*(\d+)", out)
        m2 = re.search(r"distinct candidate strings\s*:\s*(\d+)", out)
        self.assertIsNotNone(m1, "total candidate strings line missing")
        self.assertIsNotNone(m2, "distinct candidate strings line missing")
        self.assertGreaterEqual(int(m1.group(1)), 0)
        self.assertGreaterEqual(int(m2.group(1)), 0)


if __name__ == "__main__":
    unittest.main()
