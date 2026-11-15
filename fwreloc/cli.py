"""CLI entry point for fwreloc (v0.1).

Usage:
    python -m fwreloc diff OLD.BIN NEW.BIN

Prints a native-code function delta between two firmware dumps of the same
device (old, new).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fwreloc.diff import Delta, diff_firmware, format_delta, open_with_r2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fwreloc",
        description=(
            "Diff two firmware dumps of the same device (native-code "
            "function delta). Demo/analysis only."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True, help="command")

    p_diff = sub.add_parser("diff", help="compare two firmware dumps")
    p_diff.add_argument("old", type=Path, help="old firmware dump")
    p_diff.add_argument("new", type=Path, help="new firmware dump")
    p_diff.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="output format (default: text)",
    )
    # fwreloc Pro (licensed): report export + machine workflows.
    p_pro = sub.add_parser("pro", help="fwreloc Pro — licensed features")
    p_pro.add_argument(
        "--out", type=Path, default=None,
        help="default report output file (default: fwreloc_pro_report.md)",
    )
    p_pro_repo = p_pro.add_subparsers(
        dest="pro_command", required=True, help="Pro command"
    )
    p_rep = p_pro_repo.add_parser(
        "report", help="export a Markdown diff report (Pro)"
    )
    p_rep.add_argument("old", type=Path, help="old firmware dump")
    p_rep.add_argument("new", type=Path, help="new firmware dump")
    p_rep.add_argument(
        "--out", type=Path, default=None,
        help="report output file (default: fwreloc_pro_report.md)",
    )
    p_rep.add_argument(
        "--format", choices=["md", "html"], default="md",
        help="report format (default: md)",
    )
    p_rep.set_defaults(func=cmd_pro_report)
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


def json_compat(delta: Delta, old_path: Path, new_path: Path) -> None:
    print(json.dumps({
        "old": str(old_path),
        "new": str(new_path),
        "added": [f.get("name") for f in delta.added],
        "removed": [f.get("name") for f in delta.removed],
        "changed": [f.get("name") for f in delta.changed],
    }))


def check_pro_license() -> bool:
    """The Pro report feature requires a purchased license file."""
    lic = Path.home() / ".fwreloc-pro.lic"
    if lic.is_file():
        return bool(lic.read_text(encoding="utf-8").strip())
    return False


def write_pro_report(
    delta: Delta, old_path: Path, new_path: Path, out: Path, fmt: str
) -> None:
    """Write a clean Markdown (or HTML) diff report for a firmware pair."""
    if fmt == "html":
        body = _report_html(delta, old_path, new_path)
    else:
        body = _report_md(delta, old_path, new_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")


def _report_md(delta: Delta, old_path: Path, new_path: Path) -> str:
    def row(name, old, new):
        return f"| {name} | {old} | {new} |"

    lines = [
        "# fwreloc Pro — firmware diff report",
        "",
        f"- _source:_ `firmware/{old_path.name}`",
        f"- _changes:_ firmware `{new_path.name}`",
        "",
        "## Summary",
        "",
        "| Metric | Old | New |",
        "|---|---|---|",
        row("Functions", delta.old, delta.new),
        row("Added", len(delta.added), ""),
        row("Removed", "", len(delta.removed)),
        row("Changed", "", ""),
        "",
        "## Added functions",
        "",
    ]
    if delta.added:
        lines += ["| Name | Offset | Size |", "|---|---|---|"]
        lines += [
            f"| {(f.get('name') or hex(f.get('offset', 0)))} | {f.get('offset')} | {f.get('size')} |"
            for f in delta.added
        ]
    else:
        lines.append("_none_")
    lines += ["", "## Removed functions", "",]
    if delta.removed:
        lines += ["| Name | Offset | Size |", "|---|---|---|"]
        lines += [
            f"| {(f.get('name') or hex(f.get('offset', 0)))} | {f.get('offset')} | {f.get('size')} |"
            for f in delta.removed
        ]
    else:
        lines.append("_none_")
    lines += ["", "## Changed functions", "",]
    if delta.changed:
        lines += ["| Name | Old offset | New offset | Old size | New size |", "|---|---|---|---|---|"]
        lines += [
            f"| {f.get('name')} | {f.get('old_offset')} | {f.get('new_offset')} | {f.get('old_size')} | {f.get('new_size')} |"
            for f in delta.changed
        ]
    else:
        lines.append("_none_")
    lines += ["", "---", "fwreloc Pro is licensed software.", ""]
    return "\n".join(lines)


def _report_html(delta: Delta, old_path: Path, new_path: Path) -> str:
    rows = []
    for label, key in [("Added", "added"), ("Removed", "removed"),
                       ("Changed", "changed")]:
        pass
    return _report_md(delta, old_path, new_path)


def cmd_pro_report(args) -> int:
    """Pro-only: write a clean diff report for two firmware dumps."""
    if not check_pro_license():
        print(
            "fwreloc Pro: licensed copy required.", file=sys.stderr,
        )
        print(
            "Buy fwreloc Pro (https://github.com/<user>/fwreloc-pro) and "
            "place the license file at ~/.fwreloc-pro.lic",
            file=sys.stderr,
        )
        return 3

    delta = diff_firmware(args.old, args.new)
    out = args.out or Path("fwreloc_pro_report.md")
    write_pro_report(delta, args.old, args.new, out, args.format)
    print(f"wrote {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "diff":
        return cmd_diff(args)
    if args.command == "pro":
        return args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
