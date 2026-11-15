"""cutcard — SVG cut-card planner for craft tools (vinyl/CAMEO/etc.).

Usage:
    python -m tools.cutcard design.svg
    cutcard design.svg
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_RECT_TAG = re.compile(r"<rect\b[^>]*>", re.IGNORECASE)
_ATTR = re.compile(r"""((?:[\w-]+)\s*)\s*=\s*["']([^"']*)["']""")

MATERIAL_BY_COLOR = {
    "#111111": "black",
    "#222222": "dark gray",
    "#444444": "dark gray",
    "#FF0000": "red",
    "#00FF00": "green",
    "#0000FF": "blue",
    "#FFFF00": "yellow",
    "#FFFFFF": "white",
}

DEFAULT_MATERIAL = "white"


def parse_rects(xml_text: str):
    """Return a list of dicts with x, y, w, h, fill for every <rect> in the SVG."""
    rects = []
    for tag in _RECT_TAG.findall(xml_text):
        attrs = dict(_ATTR.findall(tag))
        try:
            x = float(attrs.get("x", 0))
            y = float(attrs.get("y", 0))
            w = float(attrs.get("width", 0))
            h = float(attrs.get("height", 0))
            fill = attrs.get("fill", DEFAULT_MATERIAL)
        except (TypeError, ValueError):
            continue
        if w <= 0 or h <= 0:
            continue
        rects.append({"x": x, "y": y, "w": w, "h": h, "fill": fill})
    return rects


def perimeter(rect: dict) -> float:
    """Cut length of a rectangle (perimeter), in SVG units."""
    return 2 * (rect["w"] + rect["h"])


def layer_plan(rects):
    """Group rects by color; keep first-seen order."""
    plan = []
    seen = set()
    for r in rects:
        key = r["fill"]
        if key in seen:
            continue
        seen.add(key)
        items = [rr for rr in rects if rr["fill"] == key]
        plan.append({
            "color": key,
            "material": MATERIAL_BY_COLOR.get(key, "multi"),
            "count": len(items),
            "length": sum(perimeter(r) for r in items),
        })
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cutcard",
        description="Parse an SVG and print a per-color cut-card layer plan "
                    "with an estimated cut length.",
    )
    parser.add_argument("svg", type=Path, help="SVG cut-card design")
    args = parser.parse_args(argv)

    try:
        xml = args.svg.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cutcard: cannot read {args.svg}: {exc}", file=sys.stderr)
        return 2

    rects = parse_rects(xml)
    if not rects:
        print(f"cutcard: no rectangular elements found in {args.svg}", file=sys.stderr)
        return 1

    print(f"cutcard: {args.svg}")
    print(f"  shapes    : {len(rects)}")
    print("  layers (cutting order):")
    total = 0.0
    for i, layer in enumerate(layer_plan(rects), start=1):
        total += layer["length"]
        print(
            f"    {i}. material={layer['material']:<8} color={layer['color']:<10} "
            f"shapes={layer['count']:<3} estimated_cut={layer['length']:.1f}"
        )
    print(f"  total cut length (est.) : {total:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
