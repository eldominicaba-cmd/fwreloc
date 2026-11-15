"""cutcard test suite."""

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

import tools.cutcard.main as cutcard

SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <g id="back">
    <rect x="10" y="10" width="50" height="40" fill="#111111"/>
    <rect x="80" y="10" width="40" height="60" fill="#222222"/>
    <rect x="10" y="70" width="60" height="50" fill="#FF0000"/>
    <rect x="90" y="80" width="70" height="40" fill="#00FF00" stroke="none"/>
  </g>
</svg>
"""


def _write(tmp, name, content):
    p = pathlib.Path(tmp) / name
    p.write_text(content, encoding="utf-8")
    return p


class CutCardTest(unittest.TestCase):
    def _run(self, svg_text):
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "design.svg", svg_text)
            proc = subprocess.run(
                [sys.executable, "-m", "tools.cutcard", str(p)],
                capture_output=True,
                text=True,
            )
        return proc

    def test_plan_lists_each_color_and_estimates_length(self):
        out = self._run(SVG)
        self.assertEqual(out.returncode, 0)
        self.assertIn("layers", out.stdout)
        self.assertIn("820.0", out.stdout)
        self.assertIn("#111111", out.stdout)
        self.assertIn("#222222", out.stdout)
        self.assertIn("#FF0000", out.stdout)
        self.assertIn("#00FF00", out.stdout)
        self.assertIn("estimated_cut", out.stdout)

    def test_prints_layer_order_and_materials(self):
        out = self._run(SVG)
        self.assertEqual(out.returncode, 0)
        self.assertIn("material", out.stdout)
        self.assertIn("black", out.stdout)
        self.assertIn("dark gray", out.stdout)
        self.assertIn("red", out.stdout)
        self.assertIn("green", out.stdout)

    def test_no_rects_returns_error(self):
        svg = """<?xml version="1.0"?><svg width="10" height="10"></svg>"""
        with tempfile.TemporaryDirectory() as d:
            p = _write(d, "empty.svg", svg)
            proc = subprocess.run(
                [sys.executable, "-m", "tools.cutcard", str(p)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
