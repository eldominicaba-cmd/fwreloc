# cutcard — SVG cut-card planner

cutcard parses a (mostly rectangular) SVG and prints a per-color cut-layer
plan plus an estimated cut length for vinyl/CAMEO cut-card tools.

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party Python packages are required beyond the standard library.
`radare2` is *not* needed here (that is for `fwreloc`/`salvage`).

## Usage

```sh
cutcard design.svg
python -m tools.cutcard design.svg
```

## What it does

- Finds every `<rect>` in the SVG.
- Groups them by fill colour into layers (cutting order).
- Prints an estimated cut length (perimeter sum) per layer and in total.

## What it does NOT do

- It does not nest curves, text, or raster images (only rectangular elements).
- It reports length, not kerf, material cost, or scale units.
- It is a planning aid; it does not push a machine.

## Tested on

A 200x200 SVG fixture with four rectangles (black, dark grey, red, green) —
see `tests/test_cutcard.py`. *820.0* is the arithmetic total of those four
perimeters.

## Safety

Read-only: cutcard only *reads* an SVG and prints a plan. It does not modify,
push, or distribute anything. See `SAFETY.md` at the repo root.
