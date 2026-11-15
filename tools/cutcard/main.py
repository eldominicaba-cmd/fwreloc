"""cutcard - SVG cut-card planner and PNG image tracer."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from PIL import Image

_RECT_TAG = re.compile(r"<rect\b[^>]*>", re.IGNORECASE)
_PATH_TAG = re.compile(r"<path\b[^>]*>", re.IGNORECASE)
_ATTR = re.compile(r"""([-\w]+)\s*=\s*["']([^"']*)["']""")

MATERIAL_BY_COLOR = {
    "#111111": "black", "#222222": "dark gray", "#444444": "dark gray",
    "#FF0000": "red", "#00FF00": "green", "#0000FF": "blue",
    "#FFFF00": "yellow", "#FFFFFF": "white",
}
DEFAULT_MATERIAL = "white"


def parse_shapes(xml_text):
    rects, paths = [], []
    for tag in _RECT_TAG.findall(xml_text):
        a = dict(_ATTR.findall(tag))
        try:
            r = {"kind": "rect", "x": float(a.get("x", 0)), "y": float(a.get("y", 0)),
                 "w": float(a.get("width", 0)), "h": float(a.get("height", 0)),
                 "fill": a.get("fill", DEFAULT_MATERIAL)}
        except (TypeError, ValueError):
            continue
        if r["w"] > 0 and r["h"] > 0:
            rects.append(r)
    for tag in _PATH_TAG.findall(xml_text):
        a = dict(_ATTR.findall(tag))
        d = a.get("d", "").strip()
        if d:
            paths.append({"kind": "path", "d": d, "fill": a.get("fill", DEFAULT_MATERIAL)})
    return rects, paths


def _read_num(s, i):
    start = i
    if i < len(s) and s[i] in "+-":
        i += 1
    while i < len(s) and (s[i].isdigit() or s[i] in ".eE"):
        i += 1
    return float(s[start:i]), i


def path_points(d):
    pts = []
    px = py = 0.0
    crx = cry = 0.0
    i, n = 0, len(d)
    cmd_args = {"M": 2, "m": 2, "L": 2, "l": 2, "H": 1, "h": 1,
                "V": 1, "v": 1, "C": 6, "c": 6, "S": 4, "s": 4,
                "Q": 4, "q": 4, "T": 2, "t": 2, "A": 7, "a": 7, "Z": 0}
    while i < n:
        c = d[i]
        if c in "MLHVCSQTAZmlhvcstqzad":
            cmd = c.upper()
            i += 1
            nargs = cmd_args[cmd]
            vals = []
            for _ in range(nargs):
                while i < n and d[i] in " \t\r\n":
                    i += 1
                if i < n and d[i] in "+-.0123456789":
                    v, i = _read_num(d, i)
                    vals.append(v)
                else:
                    i += 1
            if cmd in ("M", "m"):
                x = vals[0] if cmd == "M" else px + vals[0]
                y = vals[1] if cmd == "M" else py + vals[1]
                pts.append((x, y)); px, py = x, y
            elif cmd in ("L", "l"):
                x = vals[0] if cmd == "L" else px + vals[0]
                y = vals[1] if cmd == "L" else py + vals[1]
                pts.append((x, y)); px, py = x, y
            elif cmd in ("H", "h"):
                x = vals[0] if cmd == "H" else px + vals[0]
                pts.append((x, py)); px, py = x, py
            elif cmd in ("V", "v"):
                y = vals[0] if cmd == "V" else py + vals[0]
                pts.append((px, y)); px, py = px, y
            elif cmd in ("C", "c"):
                off = (0, 0) if cmd == "C" else (px, py)
                c1x, c1y = vals[0] + off[0], vals[1] + off[1]
                c2x, c2y = vals[2] + off[0], vals[3] + off[1]
                x2, y2 = vals[4] + off[0], vals[5] + off[1]
                crx, cry = x2, y2
                x1, y1 = c1x, c1y
                for tt in (0, .125, .25, .375, .5, .625, .75, .875, 1.0):
                    u = 1 - tt
                    x = (u ** 3) * x1 + 3 * (u ** 2) * tt * c1x + 3 * u * (tt ** 2) * c2x + (tt ** 3) * x2
                    y = (u ** 3) * y1 + 3 * (u ** 2) * tt * c1y + 3 * u * (tt ** 2) * c2y + (tt ** 3) * y2
                    pts.append((x, y))
                px, py = x2, y2
            elif cmd in ("S", "s"):
                off = (0, 0) if cmd == "S" else (px, py)
                c2x, c2y = vals[0] + off[0], vals[1] + off[1]
                x2, y2 = vals[2] + off[0], vals[3] + off[1]
                crx, cry = x2, y2
                c1x, c1y = 2 * px - crx, 2 * py - cry
                for tt in (0, .125, .25, .375, .5, .625, .75, .875, 1.0):
                    u = 1 - tt
                    x = (u ** 3) * c1x + 3 * (u ** 2) * tt * c2x + 3 * u * (tt ** 2) * c2x + (tt ** 3) * x2
                    y = (u ** 3) * c1y + 3 * (u ** 2) * tt * c2y + 3 * u * (tt ** 2) * c2y + (tt ** 3) * y2
                    pts.append((x, y))
                px, py = x2, y2
            elif cmd in ("Q", "q"):
                c1x = vals[0] + (px if cmd == "q" else 0)
                c1y = vals[1] + (py if cmd == "q" else 0)
                x2 = vals[2] + (px if cmd == "q" else 0)
                y2 = vals[3] + (py if cmd == "q" else 0)
                crx, cry = x2, y2
                x1, y1 = c1x, c1y
                for tt in (0, .125, .25, .375, .5, .625, .75, .875, 1.0):
                    u = 1 - tt
                    x = (u ** 2) * px + 2 * u * tt * c1x + (tt ** 2) * x2
                    y = (u ** 2) * py + 2 * u * tt * c1y + (tt ** 2) * y2
                    pts.append((x, y))
                px, py = x2, y2
            elif cmd in ("T", "t"):
                x2 = vals[0] + (px if cmd == "t" else 0)
                y2 = vals[1] + (py if cmd == "t" else 0)
                c1x, c1y = 2 * px - crx, 2 * py - cry
                crx, cry = x2, y2
                for tt in (0, .125, .25, .375, .5, .625, .75, .875, 1.0):
                    u = 1 - tt
                    x = (u ** 2) * px + 2 * u * tt * c1x + (tt ** 2) * x2
                    y = (u ** 2) * py + 2 * u * tt * c1y + (tt ** 2) * y2
                    pts.append((x, y))
                px, py = x2, y2
            elif cmd in ("A", "a"):
                rx, ry, rot, large, sweep = vals[0], vals[1], vals[2], vals[3], vals[4]
                x2, y2 = vals[5], vals[6]
                import math
                ax = x2 - px; ay = y2 - py
                ang = math.atan2(ay, ax)
                a = max(abs(rx), abs(ry)) or 1e-6
                for k in range(7):
                    t = ang + (math.pi * 2 / 6) * k
                    pts.append((px + a * math.cos(t), py + a * math.sin(t)))
                pts.append((x2, y2))
                px, py = x2, y2
            elif cmd == "Z":
                if pts and pts[-1] != (px, py):
                    pts.append((px, py))
                px, py = pts[0] if pts else (0.0, 0.0)
        else:
            i += 1
    return pts


def path_length(d):
    pts = path_points(d)
    return sum(((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
               for (ax, ay), (bx, by) in zip(pts, pts[1:]))


def perimeter(shape):
    if shape["kind"] == "rect":
        return 2 * (shape["w"] + shape["h"])
    return path_length(shape["d"])


def layer_plan(rects, paths):
    plan, seen = [], []
    for s in rects + paths:
        key = s["fill"]
        if key in seen:
            continue
        seen.append(key)
        items = [r for r in rects + paths if r["fill"] == key]
        plan.append({"kind": "shape", "color": key,
                     "material": MATERIAL_BY_COLOR.get(key, "multi"),
                     "count": len(items), "length": sum(perimeter(x) for x in items)})
    return plan


def material_size(shapes):
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    for s in shapes:
        if s["kind"] == "rect":
            pts = [(s["x"], s["y"]), (s["x"] + s["w"], s["y"]),
                   (s["x"] + s["w"], s["y"] + s["h"]), (s["x"], s["y"] + s["h"])]
        else:
            pts = path_points(s["d"])
        for x, y in pts:
            minx = min(minx, x); maxx = max(maxx, x)
            miny = min(miny, y); maxy = max(maxy, y)
    if minx == float("inf"):
        return (0, 0, 0, 0)
    return (minx, miny, maxx, maxy)


def mask_to_polygon(mask):
    from collections import defaultdict
    H, W = len(mask), len(mask[0])
    edges = []
    for y in range(H):
        for x in range(W):
            if not mask[y][x]:
                continue
            if y == 0 or not mask[y - 1][x]:
                edges.append(((x, y), (x + 1, y)))
            if y == H - 1 or not mask[y + 1][x]:
                edges.append(((x, y + 1), (x + 1, y + 1)))
            if x == 0 or not mask[y][x - 1]:
                edges.append(((x, y), (x, y + 1)))
            if x == W - 1 or not mask[y][x + 1]:
                edges.append(((x + 1, y), (x + 1, y + 1)))
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    if not adj:
        return []
    start = next(iter(adj))
    poly, cur, prev = [], start, None
    while True:
        poly.append(cur)
        nxt = [nb for nb in adj[cur] if nb != prev]
        if not nxt:
            break
        prev, cur = cur, nxt[0]
        if cur == start and len(poly) > 1:
            break
    out = []
    for p in poly:
        if not out or p != out[-1]:
            out.append(p)
    return out


def polygon_path(poly):
    if not poly:
        return ""
    return "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in poly) + " Z"


def trace_png(png_path, max_colors=8):
    img = Image.open(png_path).convert("RGB")
    w, h = img.size
    scale = max(1, int(max(w, h) / 200))
    img_small = img.resize((max(1, w // scale), max(1, h // scale)), Image.LANCZOS)
    q = img_small.quantize(colors=max_colors, method=Image.MEDIANCUT, dither=1)
    palette = q.getpalette() or []
    raw = q.tobytes()
    width, height = q.size
    idxs = sorted({raw[y * width + x] for y in range(height) for x in range(width)})
    masks = []
    for idx in idxs:
        mask = [[False] * width for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if raw[y * width + x] == idx:
                    mask[y][x] = True
        masks.append(mask)
    svg_parts, plan, total = [], [], 0.0
    bboxes = []
    for idx, mask in enumerate(masks):
        poly = mask_to_polygon(mask)
        if not poly:
            continue
        if idx * 3 + 3 <= len(palette):
            colour = "#%02X%02X%02X" % tuple(palette[idx * 3:idx * 3 + 3])
        else:
            colour = "#%02X%02X%02X" % (idx * 17 % 256, idx * 29 % 256, idx * 41 % 256)
        length = sum(((poly[i][0] - poly[i + 1][0]) ** 2 + (poly[i][1] - poly[i + 1][1]) ** 2) ** 0.5
                     for i in range(len(poly) - 1))
        material = MATERIAL_BY_COLOR.get(colour, "multi")
        plan.append({"kind": "shape", "color": colour, "material": material,
                     "count": 1, "length": length})
        svg_parts.append(f'<path d="{polygon_path(poly)}" fill="{colour}" stroke="none"/>')
        total += length
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        bboxes.append((min(xs), min(ys), max(xs), max(ys)))
    minx = min((b[0] for b in bboxes), default=0)
    miny = min((b[1] for b in bboxes), default=0)
    maxx = max((b[2] for b in bboxes), default=0)
    maxy = max((b[3] for b in bboxes), default=0)
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d' "
           "viewBox='%g %g %g %g'>%s</svg>"
           % (width, height, minx, miny, maxx, maxy, "".join(svg_parts)))
    return svg, plan, {"width": width, "height": height,
                       "bbox": (minx, miny, maxx, maxy),
                       "colours": len(idxs), "total_cut": total}


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cutcard",
        description="Parse an SVG (or trace a PNG) and print a per-colour "
                    "cut-card layer plan with cut length, travel distance and "
                    "material size.",
    )
    parser.add_argument("svg", nargs="?", type=Path,
                        help="SVG design (or omit for --trace-png)")
    parser.add_argument("--trace-png", type=Path,
                        help="PNG logo to trace into cut paths")
    parser.add_argument("--max-colors", type=int, default=8,
                        help="colour count limit for tracing (default 8)")
    parser.add_argument("--svg-out", type=Path,
                        help="write the traced SVG here (with --trace-png)")
    args = parser.parse_args(argv)

    if args.trace_png:
        svg_text, plan, info = trace_png(args.trace_png, args.max_colors)
        if args.svg_out:
            args.svg_out.write_text(svg_text, encoding="utf-8")
        print(f"cutcard: tracing {args.trace_png}")
        print(f"  source size : {info['width']} x {info['height']}")
        print(f"  colours     : {info['colours']}")
        print(f"  material    : {info['bbox'][0]:.1f} x {info['bbox'][1]:.1f} .. "
              f"{info['bbox'][2]:.1f} x {info['bbox'][3]:.1f}")
        print("  layers (cutting order):")
        tot = 0.0
        for i, layer in enumerate(plan, start=1):
            tot += layer["length"]
            print(f"    {i}. material={layer['material']:<9} colour={layer['color']:<10} "
                  f"shapes={layer['count']:<3} estimated_cut={layer['length']:.1f}")
        travel = 3 * len(plan) * 8
        print(f"  total cut length (est.) : {tot:.1f}")
        print(f"  estimated travel       : {travel:.1f}")
        return 0

    if not args.svg:
        print("cutcard: provide an SVG or --trace-png", file=sys.stderr)
        return 2
    xml = args.svg.read_text(encoding="utf-8")
    rects, paths = parse_shapes(xml)
    shapes = rects + paths
    if not shapes:
        print(f"cutcard: no rectangular or path elements in {args.svg}", file=sys.stderr)
        return 1
    print(f"cutcard: {args.svg}")
    print(f"  shapes    : {len(shapes)}")
    size = material_size(shapes)
    print(f"  material  : {size[0]:.1f} x {size[1]:.1f} .. {size[2]:.1f} x {size[3]:.1f} "
          f"({size[2]-size[0]:.1f} x {size[3]-size[1]:.1f})")
    print("  layers (cutting order):")
    tot = 0.0
    for i, layer in enumerate(layer_plan(rects, paths), start=1):
        tot += layer["length"]
        print(f"    {i}. material={layer['material']:<9} colour={layer['color']:<10} "
              f"shapes={layer['count']:<3} estimated_cut={layer['length']:.1f}")
    print(f"  total cut length (est.) : {tot:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
