"""Lightweight helpers used across the tools (no radare2 dependency)."""
import shutil
import subprocess

def resolve_r2() -> str:
    """Path to the `r2` binary on PATH (fallback: system install)."""
    return shutil.which("r2") or "/usr/bin/r2"

def run_r2(path, cmd):
    """Run `r2 -q -c <cmd> <path>` and return the CompletedProcess."""
    r2 = resolve_r2()
    proc = subprocess.run(
        [r2, "-q", "-c", cmd, str(path)],
        capture_output=True,
        text=True,
    )
    return proc
