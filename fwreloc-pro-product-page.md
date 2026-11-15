# fwreloc Pro — product page draft

> Use as the copy for a Gumroad listing, a Ko-fi product page, or a Stripe
> Payment Link. One-time price. No subscription.

---

## Product name
**fwreloc Pro — firmware diff report**

## Tagline
Two firmware dumps. One clean report on what changed.

## Price
$15 one-time (no subscription). Free `fwreloc` core stays free.

## Description
fwreloc reads two firmware dumps of the same device and reports what changed
between them: which native functions were **added**, **removed**, or
**changed**, with offsets and sizes.

The free `fwreloc diff OLD NEW` command prints that delta to the terminal.

fwreloc Pro adds a clean, ready-to-send **Markdown diff report**:

```
fwreloc pro report OLD NEW --out firmware/report.md
```

The report shows counts plus every added/removed/changed function, so you can
paste it into a GitHub issue, a changelog, or an email to your team.

## What's in the Pro download
- `fwreloc pro report` — Markdown diff report export.
- A ready-made license file (grab it right after purchase).
- The free `fwreloc diff` tool, kept free.

## Installing
1. Purchase at the link below.
2. Place the supplied license file at `~/.fwreloc-pro.lic` (or run the
   installer, which does it for you).
3. `pip install -e .` from the released zip.
4. Run `fwreloc pro report OLD NEW --out report.md`.

Requires `radare2` (`r2`) on `PATH`.

## What it does not do
- It does **not** patch binaries, emit a re-patch, or automate a firmware
  downgrade.
- It is an analysis tool: you give it two dumps and it shows you the delta.
- Retro-handheld firmware (ARM Thumb / Xtensa / MIPS, plain `.bin` with no ELF
  header) is not v1-tested — that is a v0.2 roadmap item, not current
  capability.

## Red lines
No DRM circumvention, no anti-cheat bypass, no multiplayer cheating,
no cracked-install redistribution, no online-progression modification.

## Support
Open a GitHub issue on the fwreloc repo.

---

## License asset
The purchase includes a single-user license file (`.fwreloc-pro.lic`). It is a
free-form text file — paste it wherever you keep your fwreloc config.

## Compare
| | Free `fwreloc diff` | fwreloc Pro |
|---|---|---|
| Terminal diff | yes | yes |
| Markdown report | no | yes |
| JSON machine output | yes | yes |
| License gate | no | yes |
| Price | free | $15 one-time |
