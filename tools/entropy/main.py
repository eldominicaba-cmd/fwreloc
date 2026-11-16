"""entropy - Shannon entropy / packed-content detector for binary dumps.

Usage:
    python -m tools.entropy firmware.bin
    entropy firmware.bin

What it does:
- Computes the Shannon entropy of a binary in bits per byte (0 = all identical
  bytes, 8 = fully random).
- Flags the file as "high entropy" (>= 7.0) when the content is likely packed,
  compressed or encrypted -- a common first-stop in reverse engineering.

Note: this is a heuristic signal, not proof of packing.

Red lines: same as the rest of the toolbox (no DRM circumvention, no
anti-cheat bypass, no account manipulation, no PHI storage). Singleplayer,
anti-cheat-free targets you own. Read-only.
"""
import argparse
import math
import sys
from collections import Counter
from pathlib import Path

CHUNK = 1024 * 1024
HIGH_ENTROPY = 7.0


def entropy_of(path, chunk=CHUNK):
    counter = Counter()
    total = 0
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            total += len(block)
            counter.update(block)
    if total == 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values())


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="entropy",
        description="Shannon entropy (bits per byte) of a binary dump.",
    )
    parser.add_argument("file", type=Path, help="file to scan")
    parser.add_argument("-c", "--chunk", type=int, default=CHUNK,
                        help="read chunk size in bytes (default 1 MiB)")
    args = parser.parse_args(argv)

    try:
        h = max(0.0, entropy_of(args.file, args.chunk))
    except OSError as exc:
        print(f"entropy: {args.file}: {exc}", file=sys.stderr)
        return 2

    print(f"entropy: {args.file}")
    print(f"  size        : {args.file.stat().st_size} bytes")
    print(f"  entropy     : {h:.4f} bits/byte")
    print(f"  flagged     : {'YES - likely packed/compressed/encrypted' if h >= HIGH_ENTROPY else 'no (looks like normal data)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
