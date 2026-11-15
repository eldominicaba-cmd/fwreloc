#!/usr/bin/env python3
"""fwreloc CLI (module entry)."""
import sys

def main(argv=None):
    from .cli import main as _m
    return _m(argv)

if __name__ == "__main__":
    sys.exit(main())
