# fwreloc — firmware reverse-engineering toolbox

A small, well-tested toolbox of CLI tools built on radare2, for firmware and
binary analysis, plus a craft-niche cut-card planner.

## Tools (index)

| tool | what it does |
| --- | --- |
| `fwreloc` | diffs two firmware dumps of the same device; prints the native-code function delta (added / removed / changed) via radare2 |
| `salvage` | indexes printable strings and candidate keys in a firmware/binary dump (radare2 `izzj`), sorted by frequency |
|| `savemap` | diffs two binary dumps block-by-block and reports changed regions with per-block checksums |
|| `strdiff` | diffs the printable strings between two binary dumps (added / removed / shared) |
|| `cutcard` | parses a (mostly rectangular) SVG and prints a per-color cut-card layer plan with an estimated cut length |

All tools are CLI-first and run with `python -m tools.<tool>` or the console
script after `pip install -e .`. They are part of a single monorepo so
contributors can add a new tool in minutes (see `CONTRIBUTING.md`).

## Install (dev)

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

`radare2` (`r2`) must be on `PATH` for the tools that use it (`fwreloc`,
`salvage`). It is a system package, not a pip dependency.

## Usage

```sh
# compare two firmware dumps
fwreloc diff old-fw.bin new-fw.bin
savemap old.bin new.bin

# diff printable strings between two binary dumps
strdiff old.bin new.bin

# index strings / keys in a binary
salvage firmware.bin

# plan a laser/cutting cut-card design
cutcard design.svg
```

## Scope & honesty

`fwreloc v0.1` is verified against real, versioned OpenWrt x86-64 kernel dumps
(`bzImage` 6.12.94 → 6.12.112), not retro-handheld firmware. Retro-handheld
raw `.bin` support is `v0.2` — see each tool's README.

## Red lines

- No DRM circumvention
- No anti-cheat bypass
- No multiplayer cheating / account manipulation
- No redistribution of cracked or pirated installs
- No modification of online progression or account access
- No storage of personal/PHI data

Only singleplayer, anti-cheat-free targets you own. For learning and
legitimate compatibility/migration work.
