"""CLI entry point for fwreloc (tool 1 of the monorepo).

Usage:
    python -m tools.fwreloc.cli diff OLD.BIN NEW.BIN
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .diff import Delta, diff_firmware, format_delta


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fwreloc",
        description=("Diff two firmware dumps of the same device (native-code "
                     "function delta). Demo/analysis only."),
    )
    sub = p.add_subparsers(dest="command", required=True, help="command")
    p_diff = sub.add_parser("diff", help="compare two firmware dumps")
    p_diff.add_argument("old", type=Path, help="old firmware dump")
    p_diff.add_argument("new", type=Path, help="new firmware dump")
    p_diff.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="output format",
    )
    return p


def cmd_diff(args) -> int:
    for p in (args.old, args.new):
        if not p.is_file():
            print(f"fwreloc: file not found: {p}", file=sys.stderr)
            return 2
    delta = diff_firmware(args.old, args.new)
    if args.format == "text":
        print(format_delta(delta, args.old, args.new))
    else:
        print(json_compat(delta, args.old, args.new))
    if delta.total_changed == 0:
        print("No native-code delta detected between the two dumps.")
    return 0


def json_compat(delta, old_path, new_path):
    print(json.dumps({
        "old": str(old_path), "new": str(new_path),
        "added": [f.get("name") for f in delta.added],
        "removed": [f.get("name") for f in delta.removed],
        "changed": [f.get("name") for f in delta.changed],
    }))


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "diff":
        return cmd_diff(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
