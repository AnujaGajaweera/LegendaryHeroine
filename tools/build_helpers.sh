#!/usr/bin/env bash
set -euo pipefail
cc -O2 -Wall -Wextra -o tools/prefix_path_check tools/prefix_path_check.c
