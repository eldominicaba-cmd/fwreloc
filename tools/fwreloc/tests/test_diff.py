"""fwreloc test suite.

Run from the repo root:
    python -m unittest discover -s tools -t . -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))
ROOT = Path(__file__).resolve().parent.parent.parent.parent

from tools.fwreloc.diff import diff_firmware, Delta  # noqa: E402


class FirmwareDiffTestBase(unittest.TestCase):
    fixtures = Path(__file__).resolve().parent / "fixtures"

    def _fixture(self, rel):
        return (self.fixtures / rel).resolve()


class SyntheticDiffTest(FirmwareDiffTestBase):
    def test_old_vs_new_adds_a_function(self):
        old = self._fixture("old_fw.o")
        new = self._fixture("new_fw.o")
        self.assertTrue(old.is_file(), old)
        self.assertTrue(new.is_file(), new)
        d = diff_firmware(old, new)
        self.assertEqual(d.old, 3)
        self.assertEqual(d.new, 4)
        self.assertEqual(len(d.added), 1)
        self.assertEqual(len(d.removed), 0)
        self.assertTrue(any("new_feature" in f.get("name", "") for f in d.added))


class RawFirmwareDiffTest(FirmwareDiffTestBase):
    _skip = unittest.skipUnless(
        (Path(__file__).resolve().parent / "fixtures" / "raw" / "old.bin").is_file(),
        "raw .bin fixtures not present; skipped",
    )

    @_skip
    def test_raw_old_vs_raw_new(self):
        old = self._fixture("raw/old.bin")
        new = self._fixture("raw/new.bin")
        self.assertTrue(old.is_file(), old)
        self.assertTrue(new.is_file(), new)
        d = diff_firmware(old, new)
        self.assertGreaterEqual(d.old, 1)
        self.assertGreaterEqual(d.new, 1)


class RealFirmwareDiffTest(FirmwareDiffTestBase):
    _skip = unittest.skipUnless(
        (ROOT / "firmware").is_dir(),
        "real-kernel fixture pair not present; offline-only integration test",
    )

    @_skip
    def test_real_kernels_diff(self):
        old = ROOT / "firmware" / "old_kernel.bin"
        new = ROOT / "firmware" / "new_kernel.bin"
        self.assertTrue(old.is_file(), f"missing {old}")
        self.assertTrue(new.is_file(), f"missing {new}")
        d = diff_firmware(old, new)
        self.assertGreaterEqual(d.old, 20)
        self.assertGreaterEqual(d.new, 20)
        self.assertGreater(d.total_changed, 20)


if __name__ == "__main__":
    unittest.main()
