# entropy - Shannon entropy / packed-content detector

Computes the Shannon entropy of a binary dump in bits per byte, and flags the
file when the content looks like it is packed, compressed or encrypted.

## Install

```sh
pip install -e .
```

Stdlib only — no external Python packages required. Run `pip install -e .`
from the repo root so `tools.entropy` is importable.

## Usage

```sh
entropy firmware.bin
python -m tools.entropy firmware.bin
entropy -c 2097152 big.bin   # 2 MiB chunks (for very large files)
```

## What it does

- Computes Shannon entropy (0 = all bytes identical, 8 = fully random).
- Flags `>= 7.0 bits/byte` as "likely packed/compressed/encrypted" — a common
  first-stop when hunting for custom loaders, upaders or anti-tamper.

## What it does NOT do

- It is a heuristic only — a high score does not prove packing (a random
  crypto key also scores 8.0). Corroborate with the file's section headers or a
  disassembler.
- It does not display per-section entropy (try `fwreloc`'s dump view).

## Tested on

- A real 166 KB x86-64 ELF (/bin/ls): 6.02 bits/byte (normal data, not flagged).
- A real 14 KB python binary: 1.24 bits/byte.
- A 1 MB block of `\x00`: 0.00 (correctly zero).
- 1 MB of /dev/urandom: 8.00 (flagged as packed).

## Limitations

- Chunked streaming: every byte is visited once; large files are fine, but the
  scan is I/O-bound.
- Threshold `7.0` is a placeholder; the right line differs between firmware
  (often zlib/zstd compressed), games (packed assets) and firmware (encrypted
  regions).

## Roadmap / Help wanted

- v0.2: per-section entropy tags (map entropy onto a firmware's section headers
  via radare2).
- v0.3: a `--min-run 16` mode that reports the longest run of high-entropy
  bytes (packer-tail detector).
- Help wanted: real firmware blobs and the exact thresholds used by
  different vendors.

## Safety

Read-only: entropy only *reads* a file and prints a number. It does not copy it
or modify anything.
