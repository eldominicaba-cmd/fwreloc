# savemap — binary save-file diff and region checksum diff tool

savemap diffs two binary dumps and reports changed regions with per-block
checksums, so you can locate exactly which bytes changed without dumping a full
hex diff.

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party Python packages required — only the standard library.

## Usage

```sh
savemap old.bin new.bin
python -m tools.savemap old.bin new.bin
```

## What it does

- Divides the two dumps into 16-byte blocks and checksums each block.
- Reports changed regions as RLE'd ranges.
- Prints per-block old/new checksums for differing blocks.
- Prints full-file SHA256 for both dumps.

## What it does NOT do

- It is not a function-level or disassembly diff (that is `fwreloc`).
- It reports changed regions, not a full-file hex diff.
- It is a diagnostic aid; it does not patch or generate binaries.

## Tested on

A synthetic 256-byte pair with a 6-byte change at offset 0x10..0x15
(see `tests/test_savemap.py`).
