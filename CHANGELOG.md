# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `entropy` — Shannon entropy (bits per byte) of a binary dump; flags content
  that is likely packed, compressed, or encrypted (>= 7.0 bits/byte).

## [0.1.0] — 2026-11-15

### Added
- `fwreloc` — firmware binary differ (radare2 native-function delta).
- `salvage` — printable strings / candidate keys indexer (radare2 `izzj`).
- `savemap` — block-by-block binary diff with per-block checksums.
- `strdiff` — printable-string diff between two binary dumps.
- `cutcard` — SVG cut-card layer plan + estimated cut length.
