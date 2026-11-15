#!/usr/bin/env python3
"""cutcard CLI (module entry)."""
import sys

def main(argv=None):
    from .main import main as _m
    return _m(argv)

if __name__ == "__main__":
    sys.exit(main())
