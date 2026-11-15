"""sigscan - search a binary dump for hex signatures or literal strings.

Usage:
    python -m tools.sigscan sample.bin "43 76 55" "kProtoV2"
    sigscan sample.bin --common

What it does:
- Reads a file and reports every offset where any provided pattern occurs.
- Patterns are either hex bytes (spaces or dashes are ignored) or literal
  ASCII strings.

Red lines: no DRM circumvention, no anti-cheat bypass, no account manipulation,
no redistribution of cracked/pirated installs, no PHI storage. Singleplayer,
anti-cheat-free targets you own. Read-only: sigscan never writes to the input
file and never transmits it anywhere.
"""
import argparse
import sys
from pathlib import Path


def parse_pattern(p):
    """Return (kind, needle) from a pattern string."""
    p = p.strip()
    cleaned = p.replace(" ", "").replace("-", "")
    if cleaned and all(c in "0123456789abcdefABCDEF" for c in cleaned):
        if len(cleaned) % 2:
            cleaned += "0"
        return "hex", bytes.fromhex(cleaned)
    return "ascii", p.encode("ascii", "ignore")


def find_all(data, needle):
    offsets, start = [], 0
    while True:
        i = data.find(needle, start)
        if i == -1:
            return offsets
        offsets.append(i)
        start = i + 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="sigscan",
        description="Search a binary dump for hex signatures or literal strings.",
    )
    parser.add_argument("binary", type=Path, help="binary dump to scan")
    parser.add_argument("patterns", nargs="*",
                        help="hex (e.g. 437655) or literal string to find")
    parser.add_argument("--common", action="store_true",
                        help="also search a set of common magic-byte signatures")
    args = parser.parse_args(argv)

    if not args.binary.is_file():
        print(f"sigscan: no such file: {args.binary}", file=sys.stderr)
        return 2
    data = args.binary.read_bytes()

    if args.common:
        args.patterns += ["4d5a", "7f454c46", "504b0304", "371a4530",
                          "1f8b", "2321", "ff5a", "cafebabe"]
    if not args.patterns:
        args.patterns = ["MZ", "ELF", "PK", "7z", "RAR", "BZh"]

    print(f"sigscan: {args.binary} ({len(data)} bytes)")
    found = 0
    for pat in args.patterns:
        kind, needle = parse_pattern(pat)
        offs = find_all(data, needle)
        if offs:
            found += 1
            print(f"  [{kind}] {pat!r}: {len(offs)} @ {offs[:20]}")
    if not found:
        print("  (no matches)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
