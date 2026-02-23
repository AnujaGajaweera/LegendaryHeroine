#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that a path exists and is a directory.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    path = args.path.expanduser()
    if not path.exists():
        print(f"path-check: {path}: No such file or directory")
        return 1
    if not path.is_dir():
        print(f"path-check: {path} is not a directory")
        return 1

    print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
