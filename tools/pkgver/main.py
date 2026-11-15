"""pkgver - extract and normalize version strings from a binary dump.

Usage:
    python -m tools.pkgver firmware.bin
    pkgver firmware.bin

What it does:
- Extracts printable strings (radare2 `izzj`) and reports tokens that look like
  version numbers, normalized (leading 'v' stripped) and sorted by frequency.

This fills a specific gap: other tools find strings or diff them, but pkgver
answers "what version does this dump say it is?" quickly.

Red lines: same as the rest of the toolbox (no DRM, no anti-cheat bypass,
no PHI storage). Singleplayer, anti-cheat-free targets you own.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

from shared.cli import run_r2

MIN_STR_LEN = 4

# version-like tokens: digits separated by dots, optionally with a dash
# suffix (prerelease). Leading letters (e.g. 'v' in 'v1.2.3') are stripped.
VERSION_RE = re.compile(r"\d+(?:\.\d+)+[A-Za-z0-9.-]*")


def index_strings(path, min_len=MIN_STR_LEN):
    proc = run_r2(path, "izzj")
    strings = []
    for item in json.loads(proc.stdout):
        name = (item.get("string") or "").strip()
        if len(name) >= min_len:
            strings.append(name)
    return strings


def version_candidates(strings):
    found = []
    for s in strings:
        for m in VERSION_RE.finditer(s):
            tok = m.group(0)
            if tok[0] in "vV":
                tok = tok[1:]
            if re.search(r"\d", tok):
                found.append(tok)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pkgver",
        description="Find and normalize version strings in a binary dump.",
    )
    parser.add_argument("binary", type=Path, help="binary dump")
    parser.add_argument("-n", "--top", type=int, default=20,
                        help="max versions to print (default 20)")
    args = parser.parse_args(argv)

    if not args.binary.is_file():
        print(f"pkgver: no such file: {args.binary}", file=sys.stderr)
        return 2

    strings = index_strings(args.binary)
    cands = version_candidates(strings)
    counts = collections.Counter(cands)

    print(f"pkgver: {args.binary}")
    print(f"  strings scanned : {len(strings)}")
    print(f"  version-like    : {len(cands)}")
    print("  top versions (normalized):")
    for v, c in counts.most_common(args.top):
        print(f"    {v}  (x{c})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
