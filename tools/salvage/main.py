"""salvage — index candidate strings and keys in a firmware/binary dump.

Usage:
    python -m tools.salvage path/to/dump.bin
    salvage path/to/dump.bin

Extracts printable strings with radare2, groups them by frequency, and prints
the most common ones as candidate keys, string tables or cookie constants.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

from shared.cli import run_r2

MIN_STR_LEN = 4
DEFAULT_TOP = 25


def index_strings(path, min_len=MIN_STR_LEN):
    """Return the strings radare2 finds, with their virtual addresses."""
    proc = run_r2(path, "izzj")
    strings = []
    try:
        data = json.loads(proc.stdout)
    except Exception:
        return strings
    for item in data:
        name = (item.get("string") or "").strip()
        if len(name) >= min_len:
            strings.append({
                "offset": item.get("vaddr") or item.get("addr"),
                "string": name,
            })
    return strings


def top_candidates(strings, n=DEFAULT_TOP):
    return collections.Counter(s["string"] for s in strings).most_common(n)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="salvage",
        description="Index candidate strings and keys in a binary dump.",
    )
    parser.add_argument("binary", type=Path, help="firmware/binary dump")
    parser.add_argument(
        "-n", "--top", type=int, default=DEFAULT_TOP,
        help="number of candidates to print",
    )
    args = parser.parse_args(argv)

    if not args.binary.is_file():
        print(f"salvage: file not found: {args.binary}", file=sys.stderr)
        return 2

    strings = index_strings(args.binary)
    counts = collections.Counter(s["string"] for s in strings)

    print(f"salvage: {args.binary}")
    print(f"  total candidate strings     : {len(strings)}")
    print(f"  distinct candidate strings  : {len(counts)}")
    print("\nTop 25 candidate strings (freq, offset, value):")
    for value, freq in counts.most_common(args.top):
        offset = next((s["offset"] for s in strings if s["string"] == value), None)
        print(f"  {freq:5d}  {str(offset):>10}  {value}")

    low = [v for v, c in counts.items() if len(v) <= 3 and c >= 4]
    if low:
        print("\n-short identifiers repeated >= 4x (possible packing/obfuscation):")
        for v in sorted(set(low))[:10]:
            print(f"  {v!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
