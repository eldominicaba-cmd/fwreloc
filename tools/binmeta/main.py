"""binmeta — binary fingerprint: sha256, size, magic, headers.

Usage:
    python -m tools.binmeta /bin/ls
    binmeta /bin/ls
    binmeta -f json firmware.bin

What it does:
- Computes SHA256 and reports size and file magic bytes.
- Detects ELF / PE / MZ (DOS) / Mach-O and prints key headers
  (class, endian, type, machine, entry point, section count).
- Emits raw JSON with --format json.

Red lines: no DRM circumvention, no anti-cheat bypass, no account manipulation,
no redistribution of cracked/pirated installs, no PHI storage. Singleplayer,
anti-cheat-free targets you own. Read-only.
"""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

MAGIC = {
    b"\x7fELF": "ELF",
    b"MZ": "MZ (PE/DOS)",
    b"\xca\xfe\xba\xbe": "Mach-O (universal)",
    b"\xbe\xba\xfe\xca": "Mach-O (big-endian)",
    b"%PDF": "PDF",
    b"\x1f\x8b": "gzip",
    b"\x50\x4b\x03\x04": "ZIP",
}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _le(key, off, n):
    fmt = {1: "B", 2: "H", 4: "I", 8: "Q"}[n]
    return struct.unpack_from("<" + fmt, key, off)[0]


def _be(key, off, n):
    fmt = {1: "B", 2: "H", 4: "I", 8: "Q"}[n]
    return struct.unpack_from(">" + fmt, key, off)[0]


def parse_elf(head):
    out = {}
    if head[:4] != b"\x7fELF":
        return out
    ei_class = head[4]                       # 1=ELF32, 2=ELF64
    ei_data = head[5]                        # 1=LE, 2=BE
    e_type = struct.unpack_from("<H" if ei_data == 1 else ">H", head, 0x10)[0]
    e_machine = struct.unpack_from("<H" if ei_data == 1 else ">H", head, 0x12)[0]
    e_entry = struct.unpack_from("<Q" if ei_class == 2 else "<I", head, 0x18)[0]
    e_shoff = struct.unpack_from("<Q" if ei_class == 2 else "<I", head, 0x28)[0]
    e_shnum = struct.unpack_from("<H" if ei_class == 2 else "<H", head, 0x3C)[0]
    e_shstrndx = struct.unpack_from("<H" if ei_class == 2 else "<H", head, 0x3E)[0]
    out["class"] = "ELF64" if ei_class == 2 else "ELF32"
    out["endian"] = "little" if ei_data == 1 else "big"
    out["type"] = e_type
    out["machine"] = e_machine
    out["entry"] = e_entry
    out["section_count"] = e_shnum
    out["section_index"] = e_shstrndx
    return out


def parse_pe(head):
    out = {}
    if head[:2] != b"MZ":
        return out
    pe = head[0x3C:0x3C + 0x34]
    e_lfanew = struct.unpack_from("<I", pe, 0)[0]
    opt = head[e_lfanew:e_lfanew + 0x3C]
    magic = opt[:2]                          # 0x10B = PE32, 0x10C = PE32+
    out["magic"] = "PE"
    out["machine"] = struct.unpack_from("<H", opt, 0x12)[0]
    out["number_of_sections"] = struct.unpack_from("<H", opt, 0x14)[0]
    out["size_of_optional_header"] = struct.unpack_from("<H", opt, 0x18)[0]
    out["characteristics"] = struct.unpack_from("<H", opt, 0x28)[0]
    return out


def parse_macho(head):
    out = {}
    if head[:4] not in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
        return out
    cputype = struct.unpack_from("<I" if head[6] == 0xba else ">I", head, 0x0C)[0]
    filetype = struct.unpack_from("<I" if head[6] == 0xba else ">I", head, 0x10)[0]
    out["cputype"] = cputype
    out["filetype"] = filetype
    return out


def build_fingerprint(path):
    st = path.stat()
    sha = sha256_of(path)
    with open(path, "rb") as fh:
        head = fh.read(0x400)
    result = {
        "path": str(path),
        "sha256": sha,
        "size_bytes": st.st_size,
        "magic": MAGIC.get(head[:4]) or "unknown",
        "magic_hex": head[:4].hex(),
        "format": MAGIC.get(head[:4]) or "unknown",
    }
    if head[:4] == b"\x7fELF":
        result.update(parse_elf(head))
    elif head[:2] == b"MZ":
        result.update(parse_pe(head))
    elif head[:4] in (b"\xca\xfe\xba\xbe", b"\xbe\xba\xfe\xca"):
        result.update(parse_macho(head))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="binmeta",
        description="Binary fingerprint: sha256, size, magic, build-id, section count.",
    )
    parser.add_argument("binary", type=Path, help="binary / firmware / archive")
    parser.add_argument("-f", "--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args(argv)

    try:
        fp = build_fingerprint(args.binary)
    except OSError as exc:
        print(f"binmeta: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(fp, indent=2, sort_keys=True))
        return 0

    print(f"binmeta: {fp['path']}")
    print(f"  sha256    : {fp['sha256']}")
    print(f"  size      : {fp['size_bytes']} bytes")
    print(f"  magic     : {fp['magic_hex']} ({fp['magic']})")
    print(f"  format    : {fp['format']}")
    if fp.get("class"):
        print(f"  ELF      : {fp['class']}, type={fp.get('type')}, machine=0x{fp.get('machine', 0):x}, "
              f"entry=0x{fp.get('entry', 0):x}, sections={fp.get('section_count')}")
    elif fp.get("machine"):
        print(f"  PE       : machine={fp.get('machine')}, sections={fp.get('number_of_sections')}")
    elif fp.get("cputype"):
        print(f"  Mach-O   : cputype=0x{fp['cputype']:x}, filetype=0x{fp.get('filetype')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
