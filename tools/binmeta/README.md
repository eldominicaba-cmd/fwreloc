# binmeta — binary fingerprint

binmeta fingerprints a binary: SHA256, file size, magic bytes, and — for ELF,
PE and Mach-O — key headers (class, machine, entry point, section count).

## Install

```sh
pip install -r requirements.txt
pip install -e .
```

No third-party packages beyond the standard library.

## Usage

```sh
binmeta /bin/ls
python -m tools.binmeta /bin/ls
binmeta -f json firmware.bin
```

## What it does

- Computes SHA256 and prints file size and the file's magic bytes.
- Detects ELF / PE / MZ / Mach-O and prints key headers (class, endian,
  type, machine, entry point, section count).
- Emits raw JSON with `--format json`.

## What it does NOT do

- It is not a disassembler and does not show symbols (that is
  `fwreloc`'s job via radare2).
- It does not modify or copy the input file.

## Tested on

- A real 166 KB x86-64 ELF (/bin/ls): ELF64, type=3 (EXEC), machine=0x3e
  (x86-64), 29 sections.
- A real /usr/bin/python3 (ELF64).
- A 13-byte raw binary (unknown format).

## Limitations

- Section-name extraction is limited to the string-table's first entry.
- No build-id parsing yet (planned for v0.2).
- Reads the whole file into a 1 MB-chunked stream; fine for binaries up to
  a few gigabytes but not a streaming tool.

## Roadmap / Help wanted

- v0.2: build-id parsing and DWARF section names.
- v0.3: ARM/MIPS/other-arch support verification on real firmware.
- Help wanted: realsave-game and real network-packet fixtures.

## Safety

Read-only: binmeta only *reads* a file and prints its fingerprint. It does not
modify, copy or distribute anything.
