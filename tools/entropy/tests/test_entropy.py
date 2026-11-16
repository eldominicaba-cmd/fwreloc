"""Tests for the entropy tool (Shannon entropy / packed-content detector)."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


def run_entropy(binary, extra=()):
    cmd = [sys.executable, "-m", "tools.entropy", str(binary)] + list(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)
    return proc.stdout


class EntropyTest(unittest.TestCase):
    def test_real_binary_has_plausible_entropy(self):
        out = run_entropy(pathlib.Path("/bin/ls"))
        self.assertIn("entropy", out)
        self.assertIn("6.0", out)
        self.assertIn("no (looks like normal data)", out)

    def test_all_zeros_are_zero_entropy(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(b"\x00" * 1024 * 1024)
            zero = pathlib.Path(fh.name)
        try:
            out = run_entropy(zero)
            self.assertIn("0.0000", out)
            self.assertIn("no (looks like normal data)", out)
        finally:
            zero.unlink()

    def test_random_bytes_are_high_entropy(self):
        with tempfile.NamedTemporaryFile(delete=False) as fh:
            fh.write(pathlib.Path("/dev/urandom").read_bytes()[:1024 * 1024])
            rnd = pathlib.Path(fh.name)
        try:
            out = run_entropy(rnd)
            self.assertIn("8.0000", out)
            self.assertIn("YES", out)
        finally:
            rnd.unlink()

    def test_tiny_file(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as fh:
            fh.write(b"AAAAAA")
            tiny = pathlib.Path(fh.name)
        try:
            out = run_entropy(tiny)
            self.assertIn("0.0000", out)
        finally:
            tiny.unlink()


if __name__ == "__main__":
    unittest.main()
