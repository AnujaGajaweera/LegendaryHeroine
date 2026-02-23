#!/usr/bin/env bash
set -euo pipefail

python3 -m py_compile tools/prefix_path_check.py
echo "Python helper check complete: tools/prefix_path_check.py"
