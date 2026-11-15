# sigscan — find patterns / signatures in a binary dump

sigscan reads a binary and reports every offset where a supplied hex
signature or literal string occurs.

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party packages beyond the standard library.

## Usage

```sh
sigscan sample.bin "43 76 55"        # find bytes 43 76 55
sigscan sample.bin "kProtoV2"         # find literal string
sigscan sample.bin --common           # search common magic-byte signatures
sigscan sample.bin                      # search a few common magic bytes
```

## What it does

- Searches for hex patterns (spaces/dashes ignored) and literal ASCII strings.
- Prints every offset where a pattern occurs (up to 20 shown).

## What it does NOT do

- It does not modify the input file (read-only).
- It is not a string-indexer (that is `salvage`) and not a diff (that is
  `strdiff`). It finds a few known patterns.

## Tested on

A synthetic 64-byte dump with the "MZ" magic prepended, and one case with
hex + literal patterns (see `tests/test_sigscan.py`).

## Limitations

- Output is truncated to the first 20 matches per pattern.
- Patterns are compared literally / as a raw byte sequence; multi-byte
  encodings (UTF-16 etc.) are not matched.

## Roadmap / Help wanted

- v0.2: show surrounding bytes (context window) at each match.
- v0.3: case-insensitive / regex patterns.
- Help wanted: a real firmware dump with a captured "interesting" signature in
  the test fixtures.

## Safety

Read-only: sigscan never writes to the input file and never transmits it
anywhere.
