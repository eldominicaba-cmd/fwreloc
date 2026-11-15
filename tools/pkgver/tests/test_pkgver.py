"""Tests for the pkgver tool (version-string extraction / normalization)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_pkgver(binary, *extra):
    cmd = [sys.executable, "-m", "tools.pkgver", str(binary)]
    cmd += list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


def write_dump(path, strings):
    data = b""
    for s in strings:
        data += s.encode("ascii") + b"\x00"
    path.write_bytes(data)


class PkgverTest(unittest.TestCase):
    def test_extracts_and_normalizes_version_tokens(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "fw.bin"
            write_dump(blob, [
                "fw_v1.2.3",            # -> 1.2.3
                "kVersion=2.0.1",       # -> 2.0.1
                "build_3.4.5-rc1",      # -> 3.4.5-rc1
                "libfoo.so.1",          # not version-like (no leading digit)
            ])
            out = run_pkgver(blob)
        self.assertIn("1.2.3", out)
        self.assertIn("2.0.1", out)
        self.assertIn("3.4.5-rc1", out)
        self.assertIn("strings scanned", out)
        self.assertIn("version-like", out)

    def test_ignores_non_version_strings(self):
        with tempfile.TemporaryDirectory() as d:
            blob = pathlib.Path(d) / "fw.bin"
            write_dump(blob, ["kSlotMask", "uBoot", "kProtoV2"])
            out = run_pkgver(blob)
        self.assertIn("version-like", out)
        self.assertIn("0", out)

    def test_missing_file_nonzero(self):
        with tempfile.TemporaryDirectory() as d:
            out = subprocess.run(
                [sys.executable, "-m", "tools.pkgver", "nope.bin"],
                capture_output=True, text=True,
            )
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()
