# pkgver — version-string extraction from a binary dump

pkgver extracts version-like tokens from a binary dump and prints them
normalized, sorted by frequency.

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party packages beyond the standard library (`r2pipe` pulled in by
the root `requirements.txt` for `izzj`).

## Usage

```sh
pkgver firmware.bin
python -m tools.pkgver firmware.bin
```

## What it does

- Extracts printable strings (radare2 `izzj`).
- Filters for version-like tokens: `1.2.3`, `v2.0.1`, `3.4.5-rc1`.
- Strips a leading `v` and reports the normalized token with a frequency.

## What it does NOT do

- It does not read the ELF/MZ build-id or toolchain fields (that is a header
  task, not a string task).
- It is a triage aid, not an authoritative version oracle. A dump that never
  contains a dotted numeric token will show "version-like: 0".

## Tested on

A deterministic dump containing `fw_v1.2.3`, `kVersion=2.0.1`,
`build_3.4.5-rc1` (see `tests/test_pkgver.py::PkgverTest::test_extracts_and_normalizes_version_tokens`).

## Limitations

- Version-like detection is regex based; unusual token forms are missed.
- Output is truncated to `--top` (default 20).
- No build-id or section metadata is reported.

## Roadmap / Help wanted

- v0.2: correlate a version token against a small local firmware database.
- v0.3: `--json` of the version candidates.
- Help wanted: a real firmware dump with a captured version string in the
  fixtures.

## Safety

Read-only: pkgver only *reads* a binary and prints strings. It does not
modify, patch or distribute anything.
