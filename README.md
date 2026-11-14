# fwreloc

Firmware patch reversion / compatibility tooling for retro handhelds and
singleplayer, anti-cheat-free hardware you own.

## What it does

`fwreloc diff OLD NEW` opens two firmware dumps of the *same device* with
radare2 and prints a **native-code function delta** — added, removed, and
changed functions between two firmware builds. It is a *demo and analysis*
tool.

v0.1 (this release): older/new pair → native-code delta.  
v0.2 (later): emit a machine-readable relocation/patch file to re-patch old
bootloaders/homebrew against a newer firmware revision.

## Red lines (locked, never crossed)

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
pip install -r requirements-dev.txt   # r2pipe (radare2 python bindings)
pip install -e .
```

Requires `radare2` (`r2`) on PATH.

## Usage

```sh
fwreloc diff old-fw.bin new-fw.bin
```

v0.1 only prints the delta. Patch emission (v0.2) re-writes an old
bootloader/homebrew against a newer firmware revision.

## Go / no-go

* Start with the **README** and the **Safety Contract** before touching a
  binary.
* If a request smells like a red line (DRM, anti-cheat, multiplayer, cracked
  installs, online progression), decline and log it.
* Cash bridge: 4 weeks / first $500–$1000. After that, tooling (Phase 5) is
  the destination.
