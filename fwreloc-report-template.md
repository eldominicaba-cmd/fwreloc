# fwreloc report — customer template

Single firmware pair. One report. ≤ 5 pages, technical reader.

## What we need from you (customer supplies)
- [ ] Old firmware dump (`firmware.old.bin`)
- [ ] New firmware dump (`firmware.new.bin`)
- [ ] License / ownership confirmation (you own or are authorized to analyze)
- [ ] Short context: device name + what you suspect changed
- [ ] Deadline

## Scope of work (IN SCOPE)
| Section | What it contains |
|---|---|
| Executive summary | ≤ 150-word headline of what changed |
| Diff summary | old/new function counts; added / removed / changed |
| Changed functions | name, old/new offset, old/new size, plain-English note |
| Added / removed examples | representative functions, not every function |
| Compatibility note | likely impact on game/save/battery/custom boot |
| Method + limits | tool used, scope boundaries, red lines (no patching) |

## Out of scope (NOT included)
- No binary patching, no re-patch emission, no firmware flashing
- No anti-cheat / DRM / online systems
- No multi-device or multi-firmware scale (one pair per report)
- No guarantee the re-patched firmware boots on a real device

## Report page structure
1. Title + date + firmware pair
2. Executive summary
3. Diff summary table
4. Changed functions table
5. Added / removed examples
6. Compatibility note
7. Method + limits
8. EOL + next steps

## Method note (what the tool did)
`fwreloc` compared two native-code function inventories (radare2 auto-analysis).
This is a **read-only diff** — it shows what changed between two firmware builds.
