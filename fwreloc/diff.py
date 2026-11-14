"""Radare2-backed analysis and diff core for fwreloc.

f0aremreloc compares two firmware dumps of the same device:

  * opens each dump with radare2 (r2),
  * reads native-code sections and the function inventory a bridge,
  * diffs the two inventories,
  * prints added / removed / changed functions and code regions.

This is demo/analysis only (v0.1). Full patch emission is v0.2.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BinaryInfo:
    path: Path
    container: str = "raw"
    arch: str | None = None
    bits: int | None = None
    sections: list[dict] = field(default_factory=list)
    functions: list[dict] = field(default_factory=list)
    code_section: dict | None = None

    @property
    def functions_count(self) -> int:
        return len(self.functions)


@dataclass
class Delta:
    old: int = 0
    new: int = 0
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    changed: list[dict] = field(default_factory=list)
    section_changed: bool = False

    @property
    def total_changed(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


def run_r2(path: Path, cmd: str) -> str:
    """Run one radare2 command and return stripped stdout."""
    proc = subprocess.run(
        ["r2", "-q", "-c", cmd, str(path)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        proc = subprocess.run(
            ["r2", "-2", "-q", "-c", cmd, str(path)],
            capture_output=True,
            text=True,
        )
    return proc.stdout


def open_with_r2(path: Path) -> BinaryInfo:
    info = BinaryInfo(path=path)

    meta = run_r2(path, "ij")
    try:
        m = json.loads(meta)
        binm = m.get("bin", {})
        info.container = binm.get("class") or binm.get("type") or "raw"
        info.arch = binm.get("arch") or None
        info.bits = binm.get("bits") or None
    except json.JSONDecodeError:
        pass

    secs = run_r2(path, "iSj")
    try:
        for s in json.loads(secs):
            info.sections.append(s)
            if s.get("name", "").startswith(".text") or "text" in s.get("name", ""):
                info.code_section = s
    except json.JSONDecodeError:
        pass

    # full auto-analysis in ONE r2 session so aflj sees the aaa cache.
    funcs = run_r2(path, "aaa; aflj")
    try:
        info.functions = json.loads(funcs)
    except json.JSONDecodeError:
        info.functions = []

    if not info.code_section and info.sections:
        for s in info.sections:
            if "text" in s.get("name", ""):
                info.code_section = s

    return info


def get_func_map(r2: BinaryInfo) -> dict[str, dict]:
    """Map function key -> record (name, or offset-based key)."""
    m: dict[str, dict] = {}
    for f in r2.functions:
        key = f.get("name") or f.get("nameoff") or f.get("offset")
        if key:
            m[str(key)] = f
    return m


def diff_firmware(old_path: Path, new_path: Path) -> Delta:
    old = open_with_r2(old_path)
    new = open_with_r2(new_path)

    of = get_func_map(old)
    nf = get_func_map(new)

    old_keys = {k: v for k, v in of.items()}
    new_keys = {k: v for k, v in nf.items()}

    delta = Delta(old=len(of), new=len(nf))
    for k in sorted(set(old_keys) | set(new_keys)):
        if k not in old_keys:
            delta.added.append(new_keys[k])
        elif k not in new_keys:
            delta.removed.append(old_keys[k])
        else:
            a, b = old_keys[k], new_keys[k]
            if (a.get("size") != b.get("size") or
                    a.get("offset") != b.get("offset")):
                delta.changed.append({
                    "name": a.get("name"), "old_offset": a.get("offset"),
                    "new_offset": b.get("offset"),
                    "old_size": a.get("size"), "new_size": b.get("size")})

    delta.section_changed = bool(old.code_section) != bool(new.code_section)
    return delta


def format_delta(delta: Delta, old_path: Path, new_path: Path) -> str:
    out = [
        "=" * 60,
        f"fwreloc diff  ->  old={old_path}",
        f"    new={new_path}",
        f"functions: old={delta.old}  new={delta.new}  "
        f"native_delta={delta.old + delta.new}",
        f"added={len(delta.added)}  removed={len(delta.removed)}  "
        f"changed={len(delta.changed)}",
        "=" * 60,
    ]
    if delta.added:
        out.append("\n[ADDED functions]")
        for f in delta.added[:25]:
            out.append("  + %s  size=%s" % (
                (f.get("name") or hex(f.get("offset", 0))), f.get("size")))
        if len(delta.added) > 25:
            out.append("  ... and %d more" % (len(delta.added) - 25))
    if delta.removed:
        out.append("\n[REMOVED functions]")
        for f in delta.removed[:25]:
            out.append("  - %s  size=%s" % (
                (f.get("name") or hex(f.get("offset", 0))), f.get("size")))
        if len(delta.removed) > 25:
            out.append("  ... and %d more" % (len(delta.removed) - 25))
    if delta.changed:
        out.append("\n[CHANGED functions]")
        for f in delta.changed[:25]:
            out.append("  ~ %s  old_size=%s  new_size=%s" % (
                f.get("name"), f.get("old_size"), f.get("new_size")))
        if len(delta.changed) > 25:
            out.append("  ... and %d more" % (len(delta.changed) - 25))
    return "\n".join(out)
