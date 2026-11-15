# salvage — candidate-string and key indexer

salvage indexes the printable strings in a firmware or binary dump (via
radare2) and prints the most frequent ones as candidate keys, string-table
entries and cookie constants.

## Install

```sh
pip install -r requirements.txt
pip install -e .   # or: pip install -e .[dev]
```

Requires `radare2` (`r2`) on `PATH` (system package).

## Usage

```sh
salvage firmware.bin
python -m tools.salvage firmware.bin -n 40
```

## Tested on

- OpenWrt x86-64 bzImage 6.12.94 (old) and 6.12.112 (new) — run
  `make test` in this folder.

## Safety

Read-only: salvage only *reads* a binary and prints strings. It does not
modify, patch or distribute anything. See `SAFETY.md` at the repo root.
