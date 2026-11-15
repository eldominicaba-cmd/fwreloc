"""Tests for the cutcard tool (SVG planner + PNG image tracer)."""
import io
import os
import sys
import unittest

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCutcardParse(unittest.TestCase):
    def test_rect_and_path(self):
        from tools.cutcard import main as cut
        xml = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect x="10" y="10" width="20" height="20" fill="#111111"/>
            <path d="M50 50 L80 50 L80 80 Z" fill="#FF0000"/>
            </svg>"""
        rects, paths = cut.parse_shapes(xml)
        self.assertEqual(len(rects), 1)
        self.assertEqual(len(paths), 1)
        self.assertEqual(rects[0]["w"], 20)
        self.assertEqual(paths[0]["kind"], "path")

    def test_path_length(self):
        from tools.cutcard import main as cut
        self.assertAlmostEqual(cut.path_length("M0 0 L10 0 L0 10 Z"), 24.1421, places=3)
        self.assertAlmostEqual(cut.path_length("M0 0 C10 10 0 10 20 0"), 32.67, places=2)

    def test_material_size(self):
        from tools.cutcard import main as cut
        xml = """<svg xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="10" width="20" height="20" fill="#111111"/>
            <path d="M50 50 L80 50 L80 80 Z" fill="#FF0000"/></svg>"""
        rects, paths = cut.parse_shapes(xml)
        (minx, miny, maxx, maxy) = cut.material_size(rects + paths)
        self.assertAlmostEqual(minx, 10)
        self.assertAlmostEqual(miny, 10)
        self.assertAlmostEqual(maxx, 80)
        self.assertAlmostEqual(maxy, 80)

    def test_layer_plan(self):
        from tools.cutcard import main as cut
        xml = """<svg xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="10" width="20" height="20" fill="#111111"/>
            <rect x="40" y="10" width="20" height="20" fill="#111111"/>
            <path d="M50 50 L80 50 L80 80 Z" fill="#FF0000"/></svg>"""
        rects, paths = cut.parse_shapes(xml)
        plan = cut.layer_plan(rects, paths)
        colours = {l["color"] for l in plan}
        self.assertEqual(colours, {"#111111", "#FF0000"})
        black = [l for l in plan if l["color"] == "#111111"][0]
        self.assertEqual(black["count"], 2)
        self.assertGreater(black["length"], 0)


class TestCutcardTrace(unittest.TestCase):
    def _make_logo(self, path):
        img = Image.new("RGB", (500, 500), (255, 255, 255))
        img.paste((17, 17, 17), (0, 0, 50, 110))        # black
        img.paste((0, 0, 255), (50, 0, 100, 110))       # blue
        img.paste((255, 255, 0), (100, 0, 150, 110))    # yellow
        img.paste((0, 255, 0), (150, 0, 200, 110))      # green
        img.paste((17, 17, 17), (0, 110, 100, 220))     # black 2
        img.paste((0, 0, 0), (200, 220, 300, 330))      # dark
        img.paste((0, 100, 200), (100, 150, 200, 250))  # blue 2
        tmp = Image.new("RGB", (8, 8))
        tmp.save(path, "PNG")
        with open(path, "wb") as fh:
            buf = io.BytesIO()
            img.save(buf, "PNG")
            fh.write(buf.getvalue())

    def test_trace_png(self):
        from tools.cutcard import main as cut
        tmpdir = os.path.dirname(os.path.abspath(__file__))
        png = os.path.join(tmpdir, "logo.png")
        self._make_logo(png)
        svg, plan, info = cut.trace_png(png, max_colors=8)
        self.assertGreater(info["width"], 1)
        self.assertGreater(info["height"], 1)
        self.assertGreaterEqual(info["colours"], 3)
        self.assertGreater(info["total_cut"], 0)
        self.assertGreater(len(svg), 100)
        for layer in plan:
            self.assertIn(layer["color"], str(svg))
            self.assertGreater(layer["length"], 0)

    def test_trace_png_color_count_limit(self):
        from tools.cutcard import main as cut
        tmpdir = os.path.dirname(os.path.abspath(__file__))
        png = os.path.join(tmpdir, "logo.png")
        self._make_logo(png)
        _, plan, info = cut.trace_png(png, max_colors=3)
        self.assertLessEqual(info["colours"], 3)


class TestCutcardModuleEntry(unittest.TestCase):
    def test_help_exits_zero(self):
        from tools.cutcard import main as cut
        with self.assertRaises(SystemExit) as ctx:
            cut.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
