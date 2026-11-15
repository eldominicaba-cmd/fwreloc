# strdiff — string-level diff between two binary dumps

strdiff diffs the printable strings of two binary dumps and reports what was
added, removed or retained between them.

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party Python packages required beyond the standard library
(`r2pipe` is pulled in by the root `requirements.txt`, used for `izzj`).

## Usage

```sh
strdiff old.bin new.bin
python -m tools.strdiff old.bin new.bin
```

## What it does

- Extracts printable strings from both dumps (radare2 `izzj`).
- Reports **shared**, **added** and **removed** strings.
- Optional `-n 40` caps the example listing.

## What it does NOT do

- It does not diff native functions (that is `fwreloc`).
- It does not diff blocks by checksum (that is `savemap`).
- It is a diagnostic aid; it does not patch or generate binaries.

## Tested on

A deterministic 5-string pair: `old.bin` and `new.bin` with one changed
string, one added string and no removed strings (see
`tests/test_strdiff.py::StrDiffTest::test_diff_reports_added_removed_shared`).

## Limitations

- Strings are extracted by radare2 `izzj` (min-length 4, printable-only), so
  short or non-ASCII strings are missed.
- Output is the example listing plus counts; pipe to a file for full detail.
- String extraction is content based, so a "changed" string is reported as a
  removal + an addition, not a single diff hunk.

## Roadmap / Help wanted

- v0.2: delta of repeated lines, context lines around changed strings.
- v0.3: JSON output for CI.
- Help wanted: a real two-build firmware pair with known string deltas in the
  test fixtures.

## Safety

Read-only: strdiff only *reads* two binaries and prints strings. It does not
modify, patch or distribute anything.
