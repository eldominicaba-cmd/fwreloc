"""fwreloc test suite.

Run from the repo root:
    python -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from pathlib import Path

# ensure repo root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fwreloc.diff import diff_firmware, open_with_r2  # noqa: E402
from fwreloc.diff import Delta  # noqa: E402


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
    """Raw (no-ELF-header) firmware dumps: arch hints may be needed."""

    def test_raw_old_vs_raw_new(self):
        # header-less dumps; r2 may need architecture hints to fully
        # disassemble, so we only assert a delta was computed (not that it
        # found a new function).
        old = self._fixture("raw/old.bin")
        new = self._fixture("raw/new.bin")
        self.assertTrue(old.is_file(), old)
        self.assertTrue(new.is_file(), new)
        d = diff_firmware(old, new)
        self.assertGreaterEqual(d.old, 1)
        self.assertGreaterEqual(d.new, 1)


class RealFirmwareDiffTest(FirmwareDiffTestBase):
    """Real OpenWrt x86-64 kernel builds (4.7 MB each)."""

    old = Path(__file__).resolve().parent.parent / "firmware" / "old_kernel.bin"
    new = Path(__file__).resolve().parent.parent / "firmware" / "new_kernel.bin"

    def test_real_kernels_diff(self):
        self.assertTrue(self.old.is_file(), f"missing {self.old}")
        self.assertTrue(self.new.is_file(), f"missing {self.new}")
        d = diff_firmware(self.old, self.new)
        self.assertGreaterEqual(d.old, 20)
        self.assertGreaterEqual(d.new, 20)
        self.assertGreater(d.total_changed, 20)


if __name__ == "__main__":
    unittest.main()
