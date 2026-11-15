# docs/

Documentation and reference material for the fwreloc-tools monorepo.

## Structure

- `tools/` — one self-contained CLI tool per subdirectory
  (`fwreloc`, `salvage`, `savemap`, `cutcard`).
- `shared/` — helpers used by the tools (`shared/cli.py` for radare2 calling).
- `docs/` — this folder.

## Adding a tool

See `CONTRIBUTING.md` for the exact, CI-verified steps to add a new tool.

## Console scripts

After `pip install -e .` you get:

- `fwreloc diff OLD NEW` — native-function delta between two firmware dumps
- `salvage <binary>` — string / key indexer
- `savemap <old> <new>` — binary region diff with checksums
- `cutcard <svg>` — per-color laser cut-card layer plan
