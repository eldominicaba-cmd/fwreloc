# fwreloc Pro — one-pager

## What it does
- Turns two firmware dumps into a clean Markdown diff report:
  `fwreloc pro report OLD NEW --out report.md`.
- Shows added, removed, and changed native functions with offsets and sizes.
- Free `fwreloc diff --format json` gives machine-readable output already.

## What it does NOT do
- No binary patching, no re-patch emission, no automation of firmware
  downgrades or anti-cheat bypass.
- Analysis tool, not a patch tool.
- Retro-handheld firmware (ARM Thumb / Xtensa / MIPS plain `.bin`, no ELF
  header) is NOT v1-tested — roadmap item, not current capability.

## License
- Free `fwreloc diff` — free, forever.
- `fwreloc pro report` — $15 one-time.
