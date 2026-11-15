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
- A deterministic 256 KB pair with four known diffs (offsets 0x1000,
  0x1008, 0x20000, 0x30000) — see
  `tests/test_savemap.py::SavemapDiffTest::test_realistic_large_pair_handles_known_diffs`.
  The tool reports the four RLE regions, per-block checksums and full SHA256
  digests, rc=0.

## Limitations

- Checksums are 32-bit over 16-byte blocks, so unrelated blocks can share a
  checksum (collision) — a reported region is a candidate, not a proof.
- It diffs block checksums, not content or function names (that is
  `fwreloc`). It reports *where* blocks differ, not *what*.
- Region boundaries are 16-byte block aligned, not byte precise.

## Roadmap / Help wanted

- v0.2: configurable block size, 64-bit checksums, `--json`.
- v0.3: binary diff post-processing (show differing bytes inline).
- Help wanted: a real save-file pair in the test fixtures.
