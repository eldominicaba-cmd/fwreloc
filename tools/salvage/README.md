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
- A deterministic 2 MB synthetic dump with repeated keys (see
  `tests/test_salvage.py::SalvageScanTest::test_realistic_large_binary`).
  The tool returned rc=0, printed "total candidate strings" and
  "distinct candidate strings", and surfaced all five repeated keys.

## Limitations

- Strings are extracted by radare2's `izzj`; min-length-4 and printable-only,
  so short or non-ASCII keys are missed.
- Output is the top-25 candidates; strings outside that window are not
  printed (pipe to `-n 100` if you need more).
- A dump with no printable strings of length >= 4 shows "0" and no candidates.

## Roadmap / Help wanted

- v0.2: min-length parameter, entropy-density filter for cryptographic keys,
  and optional `--json` summary.
- v0.3: scanning a directory or tar archive of dumps in one pass.
- Help wanted: a real 100 MB+ binary file for the test fixtures.

## Safety

Read-only: salvage only *reads* a binary and prints strings. It does not
modify, patch or distribute anything. See `SAFETY.md` at the repo root.
