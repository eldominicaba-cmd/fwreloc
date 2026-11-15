"""strdiff - string-level diff between two binary dumps.

Usage:
    python -m tools.strdiff old.bin new.bin
    strdiff old.bin new.bin

What it does:
- Extracts printable strings from both dumps (radare2 `izzj`), and reports the
  strings that were added, removed or retained between the two builds.

This is the complement to:
- `fwreloc` (native-function level diff),
- `savemap` (block-level diff),
- `salvage` (string index of a single dump).

Red lines: no DRM circumvention, no anti-cheat bypass, no account manipulation,
no redistribution of cracked/pirated installs, no PHI storage. Singleplayer,
anti-cheat-free targets you own.
"""
import argparse
import json
import sys
from pathlib import Path

from shared.cli import run_r2

MIN_STR_LEN = 4


def index_strings(path, min_len=MIN_STR_LEN):
    """Return the printable strings found in *path* (radare2 `izzj`)."""
    proc = run_r2(path, "izzj")
    strings = []
    for item in json.loads(proc.stdout):
        name = (item.get("string") or "").strip()
        if len(name) >= min_len:
            strings.append(name)
    return strings


def diff_strings(strings_a, strings_b):
    """Return (added, removed, shared) distinct string sets."""
    set_a = set(strings_a)
    set_b = set(strings_b)
    added = sorted(set_b - set_a)
    removed = sorted(set_a - set_b)
    shared = sorted(set_a & set_b)
    return added, removed, shared


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="strdiff",
        description="Diff the printable strings between two binary dumps.",
    )
    parser.add_argument("old", type=Path, help="first dump (baseline)")
    parser.add_argument("new", type=Path, help="second dump")
    parser.add_argument("-n", "--top", type=int, default=40,
                        help="max examples of added/removed strings (default 40)")
    args = parser.parse_args(argv)

    if not args.old.is_file() or not args.new.is_file():
        print("strdiff: missing file", file=sys.stderr)
        return 2

    strings_a = index_strings(args.old)
    strings_b = index_strings(args.new)

    added, removed, shared = diff_strings(strings_a, strings_b)

    print(f"strdiff: {args.old} -> {args.new}")
    print(f"  old  strings: {len(strings_a)}")
    print(f"  new  strings: {len(strings_b)}")
    print(f"  shared     : {len(shared)}")
    print(f"  added      : {len(added)}")
    print(f"  removed    : {len(removed)}")

    if added or removed:
        print("\nExamples of added strings:")
        for s in added[: args.top]:
            print(f"  + {s}")
        print("\nExamples of removed strings:")
        for s in removed[: args.top]:
            print(f"  - {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
