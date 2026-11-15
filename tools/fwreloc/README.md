# fwreloc — firmware binary differ

fwreloc diffs two dumps of the same device and prints the native-code function
delta (added / removed / changed functions).

## What it does

- Opens two firmware dumps with radare2 (`r2`), runs a full
  auto-analysis (`aaa`), and compares the native-function inventory of the pair.
- Prints, per pair: **added** functions, **removed** functions, **changed**
  functions (name, old/new size, old/new offset).
- Emits the change as JSON (`--format json`).

## Install (dev)

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Requires `radare2` (`r2`) on `PATH` (system package, not a pip dependency).

## Usage

```sh
fwreloc diff old-fw.bin new-fw.bin
fwreloc diff old-fw.bin new-fw.bin --format json
```

## Tested-on (truth-in-advertising)

v0.1 was verified against real, versioned firmware dumps of an x86-64 Linux
kernel (OpenWrt `fw_25.12.5.bin` → `fw_25.12.6.bin`,
`bzImage` 6.12.94 → 6.12.112): the pair yields 126 → 132 native functions
(129 added, 123 removed, 1 changed; fcn.00573240, 8 → 241 bytes).

## What it does NOT do

- Does not disassemble, patch, or patch code — it reports an inventory delta.
- Does not interpret old/new ELF sections, symbols, or relocations beyond
  native-function size/offset comparison.
- Retro-handheld raw `.bin` support is `v0.2` (roadmap).

## Scope & red lines

Singleplayer, anti-cheat-free targets you own. No DRM circumvention, no
anti-cheat bypass, no online-progression modification, no redistribution of
cracked/pirated installs, no PHI/personal-data storage.
