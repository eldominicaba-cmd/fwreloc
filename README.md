# fwreloc

Firmware patch reversion / compatibility tooling for retro handhelds and
singleplayer, anti-cheat-free hardware you own.

fwreloc **diffs two firmware dumps of the same device** and prints a
**native-code function delta** (added / removed / changed functions) so you
can see exactly what changed between two firmware builds.

- v0.1 (this release): older/new pair → native-code function delta.
- v0.2 (roadmap): retro-handheld and single-chip firmware dumps
  (ARM Thumb / Xtensa / MIPS raw .bin, no ELF header), plus full
  patch-emission to re-patch old bootloaders/homebrew against a newer
  firmware revision.

Red lines (locked, never crossed):
  * NO DRM circumvention
  * NO anti-cheat bypass
  * NO multiplayer cheating / account manipulation
  * NO redistribution of cracked/pirated installs
  * NO modification of online progression or account access
  * NO storage of personal/PHI data

Only singleplayer, anti-cheat-free targets you own. For learning and
legitimate compat/migration work.

## Install (dev)

```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Requires `radare2` (`r2`) on PATH.

## Usage

```sh
fwreloc diff old-fw.bin new-fw.bin
```

v0.1 only prints the delta. Patch emission (v0.2) re-writes an old
bootloader/homebrew against a newer firmware revision.

## Tested-on (truth-in-advertising)

fwreloc v0.1 was verified against **real, versioned firmware dumps of an
x86-64 Linux kernel**, **not** retro-handheld firmware:

```sh
$ file firmware/fw_25.12.5.bin firmware/fw_25.12.6.bin
firmware/fw_25.12.5.bin: Linux kernel x86 boot executable, bzImage, version 6.12.94 (builder@buildhost) #0 SMP Mon Jun 29 12:59:20 2026, RO-rootFS, Normal VGA, setup size 512*31, syssize 0x56840, jump 0x26c 0x8cd88ec0fc8cd239 instruction, protocol 2.15, from protected-mode code at offset 0x2c4 0x559ee4 bytes XZ compressed, relocatable, handover offset 0x561d33, legacy 64-bit entry point, can be above 4G, 64-bit EFI handoff entry point, EFI kexec boot support, xloadflags bit 5, max cmdline size 2047, init_size 0x193d000
firmware/fw_25.12.6.bin: Linux kernel x86 boot executable, bzImage, version 6.12.112 (builder@buildhost) #0 SMP Sat Oct 17 21:45:38 2026, RO-rootFS, Normal VGA, setup size 512*31, syssize 0x56d40, jump 0x26c 0x8cd88ec0fc8cd239 instruction, protocol 2.15, from protected-mode code at offset 0x2c4 0x55ef20 bytes XZ compressed, relocatable, handover offset 0x566e13, legacy 64-bit entry point, can be above 4G, 64-bit EFI handoff entry point, EFI kexec boot support, xloadflags bit 5, max cmdline size 2047, init_size 0x193d000
```

Those are the official OpenWrt x86-64 release images from two service
releases (`fw_25.12.5.bin` → `fw_25.12.6.bin`), both built by `builder@buildhost`.

**Retro-handheld firmware (ARM Thumb / Xtensa / MIPS, plain .bin, no ELF
header) is NOT tested in v0.1 and is a v0.2 roadmap item.** See "Roadmap"
below.

## Roadmap — v0.2

* Retro-handheld dumps (ARM Thumb / Xtensa / MIPS; plain .bin, no ELF
  header). Requires `--arch` hints for v0.1 (`--arch thumb --bits 32`,
  `--arch mips --bits 32`, ...).
* Real retro-handheld (single-chip, ARM Thumb / Xtensa) proof-of-work
* Patch emission (v0.2): machine-readable re-patch file for old
  bootloaders/homebrew against a newer firmware revision.

## Go / no-go

* Start with the **SAFETY.md** before touching a binary.
* If a request smells like a red line (DRM, anti-cheat, multiplayer,
  cracked installs, online progression), decline and log it.
* Cash bridge: 4 weeks / first $500–$1000. After that, tooling (Phase 5) is
  the destination.
