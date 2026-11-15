"""savemap — binary save-file diff and region checksum diff tool.

Usage:
    python -m tools.savemap OLD.BIN NEW.BIN

Divide two binary dumps into fixed-size blocks, compute a checksum per block,
and print the blocks that differ. Useful for locating exactly which bytes of a
save file or firmware blob changed without dumping a full hex diff.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

BLOCK = 16


def read_pair(old: Path, new: Path):
    return old.read_bytes(), new.read_bytes()


def changed_regions(old_b: bytes, new_b: bytes, block: int = BLOCK):
    """Return a list of (offset, length) where the two byte arrays differ.

    Byte-accurate runs, run-length encoded so a large changed block is
    reported as a single range rather than every byte tick.
    """
    n = max(len(old_b), len(new_b))
    changed = bytearray(n)
    for i in range(n):
        a = old_b[i] if i < len(old_b) else 0
        b = new_b[i] if i < len(new_b) else 0
        if a != b:
            changed[i] = 1
    runs = []
    start = None
    for i in range(n):
        if changed[i] and start is None:
            start = i
        elif not changed[i] and start is not None:
            runs.append((start, i - start))
            start = None
    if start is not None:
        runs.append((start, n - start))
    return runs


def region_checksums(old_b: bytes, new_b: bytes, block: int = BLOCK):
    rows = []
    n = max(len(old_b), len(new_b))
    for off in range(0, n, block):
        a = old_b[off:off + block]
        b = new_b[off:off + block]
        row = {
            "offset": off,
            "old_sha": a[:4].hex(),
            "new_sha": b[:4].hex(),
            "old_len": len(a),
            "new_len": len(b),
            "same": a == b,
        }
        if not row["same"]:
            rows.append(row)
    return rows


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="savemap",
        description="Diff two binary save dumps and print changed regions.",
    )
    parser.add_argument("old", type=Path, help="old save dump")
    parser.add_argument("new", type=Path, help="new save dump")
    args = parser.parse_args(argv)

    if not args.old.is_file():
        print(f"savemap: old file not found: {args.old}", file=sys.stderr)
        return 2
    if not args.new.is_file():
        print(f"savemap: new file not found: {args.new}", file=sys.stderr)
        return 2

    old_b, new_b = read_pair(args.old, args.new)

    if old_b == new_b:
        print(f"savemap: identical - no bytes differ ({len(old_b)} bytes).")
        return 0

    print(f"savemap: {args.old} -> {args.new}")
    print(f"  size old={len(old_b)}  size new={len(new_b)}")
    print("  blocks of {} bytes; report is RLE'd".format(BLOCK))

    runs = changed_regions(old_b, new_b)
    print("\n{} changed region(s):".format(len(runs)))
    for off, length in runs:
        print("  {:08x}-{:08x}  (len {})".format(off, off + length - 1, length))

    print("\nPer-block summary (only differing blocks):")
    for row in region_checksums(old_b, new_b):
        print(
            "  {:08x}  old={}  new={}  old_len={}  new_len={}".format(
                row["offset"], row["old_sha"], row["new_sha"],
                row["old_len"], row["new_len"],
            )
        )

    print("\nFull-file SHA256:")
    print("  old={}".format(hashlib.sha256(old_b).hexdigest()))
    print("  new={}".format(hashlib.sha256(new_b).hexdigest()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
